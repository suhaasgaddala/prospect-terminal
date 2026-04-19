from __future__ import annotations

from datetime import datetime, timezone

import httpx
import yfinance as yf

from app.config import get_settings
from app.db import get_database
from app.models.domain import ContentItem, Engagement
from app.services.cache_service import CacheService
from app.services.demo_data import generate_news_items, generate_score_history
from app.services.sentiment_service import SentimentService
from app.utils.text import compact_whitespace, truncate


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
        items = []
        for row in payload[:6]:
            text = compact_whitespace(row.get("summary") or row.get("headline") or "")
            if not text:
                continue
            items.append(
                ContentItem(
                    source="news",
                    ticker=ticker,
                    title=row.get("headline"),
                    text=truncate(text, 260),
                    author=row.get("source") or "Finnhub",
                    url=row.get("url") or "",
                    created_at=datetime.fromtimestamp(row.get("datetime"), tz=timezone.utc),
                    published_at=datetime.fromtimestamp(row.get("datetime"), tz=timezone.utc),
                    engagement=Engagement(score=0),
                    sentiment=self.sentiment.score_text(text),
                )
            )
        return items

    async def _fetch_yahoo_news(self, ticker: str) -> list[ContentItem]:
        ticker_obj = yf.Ticker(ticker)
        raw_news = ticker_obj.news or []
        items = []
        for row in raw_news[:6]:
            content = row.get("content", {})
            text = compact_whitespace(content.get("summary") or content.get("title") or "")
            if not text:
                continue
            published = content.get("pubDate")
            published_at = datetime.fromisoformat(published.replace("Z", "+00:00")) if published else datetime.now(timezone.utc)
            items.append(
                ContentItem(
                    source="news",
                    ticker=ticker,
                    title=content.get("title"),
                    text=truncate(text, 260),
                    author=content.get("provider", {}).get("displayName", "Yahoo Finance"),
                    url=content.get("canonicalUrl", {}).get("url") or "",
                    created_at=published_at,
                    published_at=published_at,
                    engagement=Engagement(score=0),
                    sentiment=self.sentiment.score_text(text),
                )
            )
        return items

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
