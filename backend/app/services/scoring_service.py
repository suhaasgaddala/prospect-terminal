from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Iterable

from app.config import get_settings
from app.db import get_database
from app.models.domain import ContentItem, DailyScore, ScoreComponents
from app.services.demo_data import generate_macro_history, generate_score_history
from app.services.macro_service import MacroService
from app.services.sentiment_service import SentimentService
from app.utils.math import clamp


class ScoringService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.db = get_database()
        self.sentiment = SentimentService()
        self.macro_service = MacroService()

    async def ensure_score_history(self, ticker: str, days: int = 180) -> list[DailyScore]:
        ticker = ticker.upper()
        existing = await self._fetch_existing_scores(ticker, days)
        if existing and len(existing) >= min(days, 45):
            return existing

        if self.settings.demo_mode:
            scores = generate_score_history(ticker, days)
            await self._persist_scores(scores)
            return scores

        scores = await self._compute_live_scores(ticker, days)
        await self._persist_scores(scores)
        return scores

    async def get_latest_score(self, ticker: str) -> DailyScore:
        scores = await self.ensure_score_history(ticker, 180)
        return scores[-1]

    async def _fetch_existing_scores(self, ticker: str, days: int) -> list[DailyScore]:
        try:
            floor = datetime.now(timezone.utc).date() - timedelta(days=days + 5)
            cursor = self.db["daily_scores"].find({"ticker": ticker, "date": {"$gte": floor.isoformat()}}, {"_id": 0}).sort("date", 1)
            rows = await cursor.to_list(length=days + 10)
            return [DailyScore.model_validate(row) for row in rows]
        except Exception:
            return []

    async def _compute_live_scores(self, ticker: str, days: int) -> list[DailyScore]:
        content_cursor = self.db["content_items"].find({"ticker": ticker}, {"_id": 0})
        content_items = [ContentItem.model_validate(item) async for item in content_cursor]
        filing = await self.db["filings"].find_one({"ticker": ticker}, {"_id": 0})
        price_rows = await self.db["price_bars"].find({"ticker": ticker}, {"_id": 0}).sort("date", 1).to_list(length=days + 10)
        if not price_rows:
            return generate_score_history(ticker, days)

        macro_snapshot = await self.macro_service.get_snapshot()
        price_by_date = {row["date"]: row for row in price_rows}
        today = datetime.now(timezone.utc).date()
        scores = []
        for offset in range(days):
            day = today - timedelta(days=(days - offset - 1))
            iso_day = day.isoformat()
            day_items = [item for item in content_items if item.created_at.date() == day]
            x_score = self._content_score([item for item in day_items if item.source == "x"])
            reddit_score = self._content_score([item for item in day_items if item.source == "reddit"])
            news_score = self._content_score([item for item in day_items if item.source == "news"])
            filings_score = clamp(float(filing["signal_score"])) if filing else 50.0
            components = ScoreComponents(news=news_score, x=x_score, reddit=reddit_score, filings=filings_score, macro=macro_snapshot.score)
            overall = round(
                components.news * 0.25
                + components.x * 0.20
                + components.reddit * 0.15
                + components.filings * 0.20
                + components.macro * 0.20,
                2,
            )
            price_close = float(price_by_date.get(iso_day, price_rows[min(offset, len(price_rows) - 1)])["close"])
            scores.append(
                DailyScore(
                    ticker=ticker,
                    date=day,
                    overall_score=overall,
                    components=components,
                    evidence_summary={
                        "news": f"Built from {len([item for item in day_items if item.source == 'news'])} news items.",
                        "x": f"Built from {len([item for item in day_items if item.source == 'x'])} X posts.",
                        "reddit": f"Built from {len([item for item in day_items if item.source == 'reddit'])} Reddit posts.",
                        "filings": "Latest filing score carried forward until a new filing arrives.",
                        "macro": macro_snapshot.summary,
                    },
                    price_close=price_close,
                )
            )
        return scores

    def _content_score(self, items: Iterable[ContentItem]) -> float:
        weighted = []
        for item in items:
            weight = max(1, item.engagement.score or item.engagement.likes + item.engagement.comments + item.engagement.shares)
            weighted.append((item.sentiment.score, weight))
        return self.sentiment.aggregate_sentiment(weighted)

    async def _persist_scores(self, scores: list[DailyScore]) -> None:
        try:
            collection = self.db["daily_scores"]
            for score in scores:
                payload = score.model_dump(mode="json")
                await collection.update_one({"ticker": score.ticker, "date": score.date.isoformat()}, {"$set": payload}, upsert=True)
        except Exception:
            return

    async def seed_demo_scores(self) -> None:
        for ticker in self.settings.demo_tickers:
            await self._persist_scores(generate_score_history(ticker, 365))
