from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Iterable

from app.config import get_settings
from app.db import get_database
from app.models.domain import ContentItem, DailyScore, FilingSummary, MacroSnapshot, ScoreComponents
from app.services.demo_data import generate_macro_history, generate_score_history
from app.services.macro_service import MacroService
from app.services.market_data_service import MarketDataService
from app.services.news_service import NewsService
from app.services.sec_service import SECService
from app.services.sentiment_service import SentimentService
from app.utils.math import clamp, prospect_score

SCORE_MODEL_VERSION = "historical_inputs_v2"


class ScoringService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.db = get_database()
        self.sentiment = SentimentService()
        self.macro_service = MacroService()
        self.market_data_service = MarketDataService()
        self.news_service = NewsService()
        self.sec_service = SECService()

    async def ensure_score_history(self, ticker: str, days: int = 180) -> list[DailyScore]:
        ticker = ticker.upper()
        existing = await self._fetch_existing_scores(ticker, days)
        if existing and len(existing) >= min(days, 45):
            return existing
        try:
            scores = await self._compute_live_scores(ticker, days)
            if scores:
                await self._persist_scores(scores)
                return scores
        except Exception:
            pass

        scores = generate_score_history(ticker, days)
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
            scores = [DailyScore.model_validate(row) for row in rows]
            if scores and not self._is_current_score_history(scores):
                return []
            return scores
        except Exception:
            return []

    async def _compute_live_scores(self, ticker: str, days: int) -> list[DailyScore]:
        period = self._period_for_days(days + 45)
        price_rows = await self.market_data_service.get_price_history(ticker, period=period)
        if not price_rows:
            return []

        trading_rows = price_rows[-days:]
        if len(trading_rows) < 2:
            return []

        start_date = datetime.fromisoformat(trading_rows[0]["date"]).date()
        end_date = datetime.fromisoformat(trading_rows[-1]["date"]).date()
        news_items = await self.news_service.get_historical_news(ticker, start_date - timedelta(days=7), end_date)
        filings = await self.sec_service.get_filing_history(ticker, years=4, limit=12)
        macro_history = await self.macro_service.get_history(start_date, end_date)

        scores = []
        last_macro: MacroSnapshot | None = None
        for row in trading_rows:
            day = datetime.fromisoformat(row["date"]).date()
            trailing_news = [
                item for item in news_items if day - timedelta(days=6) <= item.created_at.date() <= day
            ]
            news_score = self._historical_news_score(trailing_news, day)
            filing = self._latest_filing_for_day(filings, day)
            filings_score = filing.signal_score if filing else 50.0
            last_macro = self._latest_macro_for_day(macro_history, day, last_macro)
            macro_score = last_macro.score if last_macro else generate_macro_history(1)[-1].score
            components = ScoreComponents(
                news=news_score,
                x=50.0,
                reddit=50.0,
                filings=filings_score,
                macro=macro_score,
            )
            overall = prospect_score(components.news, components.filings, components.macro)
            price_close = float(row["close"])
            scores.append(
                DailyScore(
                    ticker=ticker,
                    date=day,
                    overall_score=overall,
                    components=components,
                    evidence_summary={
                        "model_version": SCORE_MODEL_VERSION,
                        "news": f"Built from {len(trailing_news)} real historical news item(s) available through {day.isoformat()}.",
                        "x": "Social Pulse is preview-only and is not included in the Prospect Score.",
                        "reddit": "Social Pulse is preview-only and is not included in the Prospect Score.",
                        "filings": (
                            f"Carried forward from {filing.form_type} filed on {filing.filed_at.date().isoformat()}."
                            if filing
                            else "No historical filing was available yet; filing score stayed neutral."
                        ),
                        "macro": last_macro.summary if last_macro else "Historical macro context was unavailable; neutral fallback applied.",
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

    def _historical_news_score(self, items: Iterable[ContentItem], day: date) -> float:
        weighted = []
        for item in items:
            age_days = max((day - item.created_at.date()).days, 0)
            recency_weight = max(0.5, 2.0 - age_days * 0.25)
            engagement_weight = max(1, item.engagement.score or item.engagement.likes + item.engagement.comments + item.engagement.shares)
            weighted.append((item.sentiment.score, recency_weight * engagement_weight))
        return self.sentiment.aggregate_sentiment(weighted)

    def _latest_filing_for_day(self, filings: list[FilingSummary], day: date) -> FilingSummary | None:
        eligible = [filing for filing in filings if filing.filed_at.date() <= day]
        return eligible[0] if eligible else None

    def _latest_macro_for_day(
        self,
        history: list[MacroSnapshot],
        day: date,
        last_macro: MacroSnapshot | None,
    ) -> MacroSnapshot | None:
        eligible = [snapshot for snapshot in history if snapshot.as_of.date() <= day]
        return eligible[-1] if eligible else last_macro

    def _period_for_days(self, days: int) -> str:
        if days <= 95:
            return "3mo"
        if days <= 185:
            return "6mo"
        if days <= 370:
            return "1y"
        if days <= 740:
            return "2y"
        return "5y"

    def _is_current_score_history(self, scores: list[DailyScore]) -> bool:
        if not scores:
            return False
        has_neutral_social = all(
            abs(score.components.x - 50.0) < 0.01 and abs(score.components.reddit - 50.0) < 0.01
            for score in scores
        )
        has_version = all(score.evidence_summary.get("model_version") == SCORE_MODEL_VERSION for score in scores)
        has_trading_day_dates = all(score.date.weekday() < 5 for score in scores)
        return has_neutral_social and has_version and has_trading_day_dates
