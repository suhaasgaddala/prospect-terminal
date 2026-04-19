from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import httpx
import yfinance as yf

from app.config import get_settings
from app.db import get_database
from app.models.domain import ContentItem, Engagement
from app.services.cache_service import CacheService
from app.services.demo_data import generate_news_items, generate_score_history
from app.services.sentiment_service import SentimentService
from app.utils.text import compact_whitespace, truncate

_TICKER_ALIASES: dict[str, tuple[str, ...]] = {
    "AAPL": ("apple", "iphone", "ipad", "mac"),
    "MSFT": ("microsoft", "azure", "windows"),
    "NVDA": ("nvidia", "geforce", "cuda"),
    "TSLA": ("tesla", "elon musk"),
    "AMD": ("advanced micro devices", "amd", "ryzen"),
    "META": ("meta", "facebook", "instagram"),
    "AMZN": ("amazon", "aws"),
    "GOOGL": ("alphabet", "google", "youtube"),
    "PLTR": ("palantir",),
    "NFLX": ("netflix",),
    "JPM": ("jpmorgan", "jpmorgan chase"),
    "SMCI": ("super micro", "supermicro"),
}


class NewsService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.cache = CacheService()
        self.db = get_database()
        self.sentiment = SentimentService()

    async def get_news(self, ticker: str) -> list[ContentItem]:
        ticker = ticker.upper()
        items = []
        try:
            if self.settings.finnhub_api_key:
                items = await self._fetch_finnhub_news(ticker)
            if not items:
                items = await self._fetch_yahoo_news(ticker)
        except Exception:
            items = []

        if items:
            serialized = [item.model_dump(mode="json") for item in items]
            try:
                await self.cache.set_cached_document("content_cache", f"news:{ticker}", {"items": serialized}, "news", ttl_minutes=45)
            except Exception:
                pass
            await self._persist_items(items)
            return items

        try:
            cached, _ = await self.cache.stale_or_none("content_cache", f"news:{ticker}")
            if cached:
                return [ContentItem.model_validate(item) for item in cached.get("items", [])]
        except Exception:
            pass
        return generate_news_items(ticker, generate_score_history(ticker))

    async def get_historical_news(self, ticker: str, start_date: date, end_date: date) -> list[ContentItem]:
        ticker = ticker.upper()
        live_items: list[ContentItem] = []
        if self.settings.finnhub_api_key:
            try:
                live_items = await self._fetch_finnhub_news_range(ticker, start_date, end_date)
            except Exception:
                live_items = []

        if live_items:
            await self._persist_items(live_items)
            return live_items

        try:
            cursor = self.db["content_items"].find(
                {
                    "ticker": ticker,
                    "source": "news",
                    "created_at": {
                        "$gte": datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc).isoformat(),
                        "$lte": datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc).isoformat(),
                    },
                },
                {"_id": 0},
            ).sort("created_at", 1)
            cached_items = [ContentItem.model_validate(item) async for item in cursor]
            if cached_items:
                return cached_items
        except Exception:
            pass

        return []

    def news_score(self, items: list[ContentItem]) -> float:
        weighted = []
        now = datetime.now(timezone.utc)
        for item in items:
            age_hours = max((now - item.created_at).total_seconds() / 3600, 0)
            recency_weight = max(0.5, 2.5 - min(age_hours / 72, 2.0))
            weighted.append((item.sentiment.score, recency_weight))
        return self.sentiment.aggregate_sentiment(weighted)

    async def _fetch_finnhub_news(self, ticker: str) -> list[ContentItem]:
        today = datetime.now(timezone.utc).date()
        start = today.replace(day=max(1, today.day - 7))
        url = "https://finnhub.io/api/v1/company-news"
        params = {
            "symbol": ticker,
            "from": start.isoformat(),
            "to": today.isoformat(),
            "token": self.settings.finnhub_api_key,
        }
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
        return self._select_top_items(ticker, self._normalize_finnhub_rows(ticker, payload[:15]))

    async def _fetch_finnhub_news_range(self, ticker: str, start_date: date, end_date: date) -> list[ContentItem]:
        url = "https://finnhub.io/api/v1/company-news"
        params = {
            "symbol": ticker,
            "from": start_date.isoformat(),
            "to": end_date.isoformat(),
            "token": self.settings.finnhub_api_key,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
        return self._dedupe_items(self._normalize_finnhub_rows(ticker, payload))

    async def _fetch_yahoo_news(self, ticker: str) -> list[ContentItem]:
        ticker_obj = yf.Ticker(ticker)
        raw_news = ticker_obj.news or []
        items = []
        for row in raw_news[:15]:
            content = row.get("content", {})
            title = compact_whitespace(content.get("title") or "")
            text = compact_whitespace(content.get("summary") or title)
            url = content.get("canonicalUrl", {}).get("url") or ""
            if not text or not title or not url:
                continue
            published = content.get("pubDate")
            published_at = datetime.fromisoformat(published.replace("Z", "+00:00")) if published else datetime.now(timezone.utc)
            items.append(
                ContentItem(
                    source="news",
                    ticker=ticker,
                    title=title,
                    text=truncate(text, 260),
                    author=content.get("provider", {}).get("displayName", "Yahoo Finance"),
                    url=url,
                    created_at=published_at,
                    published_at=published_at,
                    engagement=Engagement(score=0),
                    sentiment=self.sentiment.score_text(text),
                )
            )
        return self._select_top_items(ticker, items)

    async def _persist_items(self, items: list[ContentItem]) -> None:
        if not items:
            return
        try:
            collection = self.db["content_items"]
            for item in items:
                await collection.update_one(
                    {"source": item.source, "ticker": item.ticker, "url": item.url},
                    {"$set": item.model_dump(mode="json")},
                    upsert=True,
                )
        except Exception:
            return

    def _normalize_finnhub_rows(self, ticker: str, rows: list[dict]) -> list[ContentItem]:
        items = []
        for row in rows:
            text = compact_whitespace(row.get("summary") or row.get("headline") or "")
            title = compact_whitespace(row.get("headline") or "")
            url = row.get("url") or ""
            published_at = datetime.fromtimestamp(row.get("datetime"), tz=timezone.utc)
            if not text or not title or not url:
                continue
            items.append(
                ContentItem(
                    source="news",
                    ticker=ticker,
                    title=title,
                    text=truncate(text, 260),
                    author=row.get("source") or "Finnhub",
                    url=url,
                    created_at=published_at,
                    published_at=published_at,
                    engagement=Engagement(score=0),
                    sentiment=self.sentiment.score_text(text),
                )
            )
        return items

    def _dedupe_items(self, items: list[ContentItem]) -> list[ContentItem]:
        deduped: list[ContentItem] = []
        seen_urls: set[str] = set()
        seen_titles: set[str] = set()
        for item in sorted(items, key=lambda current: current.published_at or current.created_at):
            url_key = item.url.strip().lower()
            title_key = compact_whitespace((item.title or "").lower())
            if not url_key or not title_key:
                continue
            if url_key in seen_urls or title_key in seen_titles:
                continue
            seen_urls.add(url_key)
            seen_titles.add(title_key)
            deduped.append(item)
        return deduped

    def _select_top_items(self, ticker: str, items: list[ContentItem], limit: int = 6) -> list[ContentItem]:
        if not items:
            return []
        deduped = self._dedupe_items(items)

        ranked = sorted(
            deduped,
            key=lambda item: (
                self._relevance_score(ticker, item),
                item.published_at or item.created_at,
            ),
            reverse=True,
        )
        relevant = [item for item in ranked if self._relevance_score(ticker, item) > 0]
        selected = relevant[:limit]
        if len(selected) < min(limit, 3):
            for item in ranked:
                if item in selected:
                    continue
                selected.append(item)
                if len(selected) >= limit:
                    break
        return selected[:limit]

    def _relevance_score(self, ticker: str, item: ContentItem) -> int:
        ticker = ticker.upper()
        haystack = " ".join(
            [
                (item.title or ""),
                item.text,
                item.author,
                item.url,
            ]
        ).lower()
        score = 0
        ticker_lower = ticker.lower()
        if ticker_lower in (item.title or "").lower():
            score += 5
        if ticker_lower in item.text.lower():
            score += 3
        if f"/{ticker_lower}" in item.url.lower() or f"-{ticker_lower}-" in item.url.lower():
            score += 2
        for alias in _TICKER_ALIASES.get(ticker, ()):
            if alias in (item.title or "").lower():
                score += 4
            elif alias in haystack:
                score += 2
        return score
