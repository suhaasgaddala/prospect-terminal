from __future__ import annotations

from datetime import datetime, timezone

from app.config import get_settings
from app.db import get_database
from app.models.api import LeaderboardResponse
from app.models.domain import LeaderboardEntry
from app.services.demo_data import COMPANY_NAMES, generate_score_history, generate_thesis, latest_quote_from_scores


class LeaderboardService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.db = get_database()

    async def get_leaderboard(self) -> LeaderboardResponse:
        if self.settings.demo_mode:
            entries = []
            for ticker in self.settings.demo_tickers:
                scores = generate_score_history(ticker)
                quote = latest_quote_from_scores(ticker, scores)
                thesis = generate_thesis(ticker, scores)
                entries.append(
                    LeaderboardEntry(
                        ticker=ticker,
                        company_name=COMPANY_NAMES.get(ticker, ticker),
                        price=quote.price,
                        daily_change_percent=quote.daily_change_percent,
                        overall_score=scores[-1].overall_score,
                        thesis_rating=thesis.rating,
                    )
                )
            bullish = sorted(entries, key=lambda entry: entry.overall_score, reverse=True)[:6]
            bearish = sorted(entries, key=lambda entry: entry.overall_score)[:6]
            return LeaderboardResponse(bullish=bullish, bearish=bearish, updated_at=datetime.now(timezone.utc))

        latest_rows = await self.db["daily_scores"].aggregate(
            [
                {"$sort": {"date": -1}},
                {"$group": {"_id": "$ticker", "doc": {"$first": "$$ROOT"}}},
            ]
        ).to_list(length=100)
        entries = []
        for row in latest_rows:
            doc = row["doc"]
            quote = await self.db["quotes"].find_one({"ticker": doc["ticker"]}, {"_id": 0})
            thesis = await self.db["theses"].find_one({"ticker": doc["ticker"]}, {"_id": 0})
            if not quote:
                continue
            entries.append(
                LeaderboardEntry(
                    ticker=doc["ticker"],
                    company_name=quote.get("company_name", doc["ticker"]),
                    price=quote.get("price", 0),
                    daily_change_percent=quote.get("daily_change_percent", 0),
                    overall_score=doc.get("overall_score", 50),
                    thesis_rating=(thesis or {}).get("rating", "neutral"),
                )
            )
        bullish = sorted(entries, key=lambda entry: entry.overall_score, reverse=True)[:6]
        bearish = sorted(entries, key=lambda entry: entry.overall_score)[:6]
        return LeaderboardResponse(bullish=bullish, bearish=bearish, updated_at=datetime.now(timezone.utc))
