from __future__ import annotations

from datetime import datetime, timezone

from app.config import get_settings
from app.db import get_database
from app.models.api import LeaderboardResponse
from app.models.domain import LeaderboardEntry, Quote
from app.services.demo_data import COMPANY_NAMES, generate_score_history, generate_thesis, latest_quote_from_scores
from app.services.market_data_service import MarketDataService
from app.services.scoring_service import ScoringService


class LeaderboardService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.db = get_database()
        self.market_data_service = MarketDataService()
        self.scoring_service = ScoringService()

    async def get_leaderboard(self) -> LeaderboardResponse:
        latest_rows = await self.db["daily_scores"].aggregate(
            [
                {"$sort": {"date": -1}},
                {"$group": {"_id": "$ticker", "doc": {"$first": "$$ROOT"}}},
            ]
        ).to_list(length=100)
        latest_scores = {row["doc"]["ticker"]: row["doc"] for row in latest_rows}
        tickers = list(dict.fromkeys([*self.settings.demo_tickers, *latest_scores.keys()]))
        quote_rows = await self.db["quotes"].find({"ticker": {"$in": tickers}}, {"_id": 0}).to_list(length=len(tickers) + 5)
        quotes_by_ticker = {row["ticker"]: Quote.model_validate(row) for row in quote_rows}

        entries = []
        for ticker in tickers:
            score_doc = latest_scores.get(ticker)
            if score_doc is None:
                try:
                    scores = await self.scoring_service.ensure_score_history(ticker, 180)
                    if scores:
                        score_doc = scores[-1].model_dump(mode="json")
                except Exception:
                    score_doc = None

            quote = quotes_by_ticker.get(ticker)
            if quote is None:
                try:
                    quote = await self.market_data_service.get_quote(ticker)
                except Exception:
                    if score_doc is not None:
                        scores = generate_score_history(ticker)
                        quote = latest_quote_from_scores(ticker, scores)
                    else:
                        continue

            thesis = await self.db["theses"].find_one({"ticker": ticker}, {"_id": 0})
            thesis_rating = (thesis or {}).get("rating")
            if thesis_rating is None:
                fallback_scores = generate_score_history(ticker)
                thesis_rating = generate_thesis(ticker, fallback_scores).rating

            entries.append(
                LeaderboardEntry(
                    ticker=ticker,
                    company_name=quote.company_name or COMPANY_NAMES.get(ticker, ticker),
                    price=quote.price,
                    daily_change_percent=quote.daily_change_percent,
                    overall_score=(score_doc or {}).get("overall_score", generate_score_history(ticker)[-1].overall_score),
                    thesis_rating=thesis_rating,
                )
            )
        bullish = sorted(entries, key=lambda entry: entry.overall_score, reverse=True)[:6]
        bearish = sorted(entries, key=lambda entry: entry.overall_score)[:6]
        return LeaderboardResponse(bullish=bullish, bearish=bearish, updated_at=datetime.now(timezone.utc))
