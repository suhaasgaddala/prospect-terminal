from __future__ import annotations

import asyncio
import math
from datetime import datetime, timezone

from app.config import get_settings
from app.db import get_database
from app.models.api import LeaderboardResponse
from app.models.domain import LeaderboardEntry, Quote
from app.services.demo_data import COMPANY_NAMES, generate_score_history, generate_thesis, latest_quote_from_scores
from app.services.market_data_service import MarketDataService


class LeaderboardService:
    NON_STOCK_KEYWORDS = (" etf", " fund", " trust", " index", " spdr", " ishares", " vanguard")
    LEADERBOARD_TICKERS = (
        "AAPL",
        "MSFT",
        "NVDA",
        "AMD",
        "INTC",
        "AVGO",
        "QCOM",
        "META",
        "AMZN",
        "GOOGL",
        "NFLX",
        "PLTR",
        "ORCL",
        "CRM",
        "ADBE",
        "SHOP",
        "UBER",
        "TSLA",
        "DIS",
        "COST",
        "WMT",
        "KO",
        "PEP",
        "JPM",
        "BAC",
        "GS",
        "C",
        "XOM",
        "CVX",
        "CAT",
        "BA",
        "GE",
        "RTX",
        "UNH",
        "PFE",
        "JNJ",
        "MRK",
        "ABBV",
        "LLY",
        "VZ",
        "TMUS",
        "T",
    )

    def __init__(self) -> None:
        self.settings = get_settings()
        self.db = get_database()
        self.market_data_service = MarketDataService()

    async def get_leaderboard(self) -> LeaderboardResponse:
        latest_rows = await self.db["daily_scores"].aggregate(
            [
                {"$sort": {"date": -1}},
                {"$group": {"_id": "$ticker", "doc": {"$first": "$$ROOT"}}},
            ]
        ).to_list(length=100)
        latest_scores = {row["doc"]["ticker"]: row["doc"] for row in latest_rows}
        tickers = self._eligible_tickers()
        quote_rows = await self.db["quotes"].find({"ticker": {"$in": tickers}}, {"_id": 0}).to_list(length=len(tickers) + 5)
        quotes_by_ticker = {row["ticker"]: Quote.model_validate(row) for row in quote_rows}
        missing_quote_tickers = [ticker for ticker in tickers if ticker not in quotes_by_ticker]
        if missing_quote_tickers:
            fetched_quotes = await asyncio.gather(
                *(self.market_data_service.get_quote(ticker) for ticker in missing_quote_tickers),
                return_exceptions=True,
            )
            for ticker, result in zip(missing_quote_tickers, fetched_quotes):
                if isinstance(result, Exception):
                    continue
                quotes_by_ticker[ticker] = result

        entries = []
        for ticker in tickers:
            score_doc = latest_scores.get(ticker)
            if score_doc is None:
                score_doc = generate_score_history(ticker)[-1].model_dump(mode="json")

            quote = quotes_by_ticker.get(ticker)
            if quote is None:
                scores = generate_score_history(ticker)
                quote = latest_quote_from_scores(ticker, scores)
            if not self._is_eligible_stock(ticker, quote.company_name):
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

        recent_returns = await self._recent_return_map([entry.ticker for entry in entries] + ["SPY"], sessions=5)
        spy_quote = await self._get_spy_quote()
        spy_change = spy_quote.daily_change_percent if spy_quote else 0.0
        spy_recent_return = recent_returns.get("SPY")
        bullish_candidates = [
            entry for entry in entries if self._is_bullish(entry, spy_change, recent_returns.get(entry.ticker), spy_recent_return)
        ]
        strict_bearish = [
            entry for entry in entries if self._is_bearish(entry, spy_change, recent_returns.get(entry.ticker), spy_recent_return)
        ]
        secondary_cutoff = self._score_cutoff(entries, bottom_fraction=0.4)
        secondary_bearish = [
            entry
            for entry in entries
            if entry.ticker not in {item.ticker for item in strict_bearish}
            and self._is_secondary_bearish(
                entry,
                spy_change,
                recent_returns.get(entry.ticker),
                spy_recent_return,
                secondary_cutoff,
            )
        ]

        bullish = sorted(
            bullish_candidates,
            key=lambda entry: (
                entry.overall_score,
                entry.daily_change_percent - spy_change,
                entry.daily_change_percent,
            ),
            reverse=True,
        )[:6]
        bearish_pool = strict_bearish + secondary_bearish
        bearish = sorted(
            bearish_pool,
            key=lambda entry: self._bearish_rank(
                entry,
                spy_change,
                recent_returns.get(entry.ticker),
                spy_recent_return,
            ),
            reverse=True,
        )[:6]
        return LeaderboardResponse(bullish=bullish, bearish=bearish, updated_at=datetime.now(timezone.utc))

    async def _get_spy_quote(self) -> Quote | None:
        try:
            cached = await self.db["quotes"].find_one({"ticker": "SPY"}, {"_id": 0})
            if cached:
                return Quote.model_validate(cached)
        except Exception:
            pass
        try:
            return await self.market_data_service.get_quote("SPY")
        except Exception:
            return None

    def _is_bullish(
        self,
        entry: LeaderboardEntry,
        spy_change: float,
        recent_return: float | None,
        spy_recent_return: float | None,
    ) -> bool:
        relative_strength = entry.daily_change_percent - spy_change
        relative_recent = (
            (recent_return - spy_recent_return)
            if recent_return is not None and spy_recent_return is not None
            else None
        )
        return (
            entry.overall_score >= 60
            or (
                entry.thesis_rating == "bullish"
                and entry.overall_score >= 55
                and (
                    entry.daily_change_percent >= 0
                    or relative_strength >= 0.25
                    or (relative_recent is not None and relative_recent >= 0.75)
                )
            )
        )

    def _is_bearish(
        self,
        entry: LeaderboardEntry,
        spy_change: float,
        recent_return: float | None,
        spy_recent_return: float | None,
    ) -> bool:
        relative_strength = entry.daily_change_percent - spy_change
        relative_recent = (
            (recent_return - spy_recent_return)
            if recent_return is not None and spy_recent_return is not None
            else None
        )
        bearish_conviction = (
            entry.overall_score <= 45
            or (entry.thesis_rating == "bearish" and entry.overall_score < 50)
        )
        weak_tape = (
            entry.daily_change_percent < 0
            or relative_strength <= -0.75
            or (relative_recent is not None and relative_recent <= -2.0)
        )
        return bearish_conviction and weak_tape

    def _is_secondary_bearish(
        self,
        entry: LeaderboardEntry,
        spy_change: float,
        recent_return: float | None,
        spy_recent_return: float | None,
        score_cutoff: float,
    ) -> bool:
        relative_strength = entry.daily_change_percent - spy_change
        relative_recent = (
            (recent_return - spy_recent_return)
            if recent_return is not None and spy_recent_return is not None
            else None
        )
        if entry.thesis_rating == "bullish" and entry.overall_score >= 58:
            return False
        if entry.overall_score > score_cutoff:
            return False
        if entry.daily_change_percent > 0.75 and relative_strength > -0.25:
            return False
        return (
            entry.daily_change_percent < 0.5
            and (
                relative_strength <= -0.5
                or entry.daily_change_percent < 0
                or (relative_recent is not None and relative_recent <= -1.0)
            )
        )

    def _bearish_rank(
        self,
        entry: LeaderboardEntry,
        spy_change: float,
        recent_return: float | None,
        spy_recent_return: float | None,
    ) -> tuple[float, float, float]:
        relative_strength = entry.daily_change_percent - spy_change
        relative_recent = (
            (recent_return - spy_recent_return)
            if recent_return is not None and spy_recent_return is not None
            else 0.0
        )
        thesis_bonus = 10.0 if entry.thesis_rating == "bearish" else -8.0 if entry.thesis_rating == "bullish" else 0.0
        weakness_score = (100 - entry.overall_score) + max(-relative_strength, 0) * 6 + max(-relative_recent, 0) * 2 + max(-entry.daily_change_percent, 0) * 3 + thesis_bonus
        return (
            weakness_score,
            -entry.overall_score,
            -entry.daily_change_percent,
        )

    def _eligible_tickers(self) -> list[str]:
        return list(dict.fromkeys(ticker.upper() for ticker in self.LEADERBOARD_TICKERS))

    def _is_eligible_stock(self, ticker: str, company_name: str) -> bool:
        if ticker not in set(self._eligible_tickers()):
            return False
        name = f" {company_name.lower()} "
        return not any(keyword in name for keyword in self.NON_STOCK_KEYWORDS)

    def _score_cutoff(self, entries: list[LeaderboardEntry], bottom_fraction: float) -> float:
        if not entries:
            return 55.0
        scores = sorted(entry.overall_score for entry in entries)
        index = max(0, min(len(scores) - 1, math.ceil(len(scores) * bottom_fraction) - 1))
        return scores[index]

    async def _recent_return_map(self, tickers: list[str], sessions: int = 5) -> dict[str, float]:
        returns: dict[str, float] = {}
        unique_tickers = list(dict.fromkeys(ticker.upper() for ticker in tickers))
        for ticker in unique_tickers:
            try:
                rows = await self.db["price_bars"].find({"ticker": ticker}, {"_id": 0}).sort("date", -1).to_list(length=sessions + 1)
            except Exception:
                rows = []
            if len(rows) < sessions + 1:
                continue
            latest_close = float(rows[0]["close"])
            prior_close = float(rows[sessions]["close"])
            if prior_close:
                returns[ticker] = round(((latest_close / prior_close) - 1) * 100, 2)
        return returns
