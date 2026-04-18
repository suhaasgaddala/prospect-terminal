from __future__ import annotations

from datetime import datetime, timezone

import yfinance as yf

from app.config import get_settings
from app.db import get_database
from app.models.domain import Quote
from app.services.cache_service import CacheService
from app.services.demo_data import generate_score_history, latest_quote_from_scores
from app.utils.math import pct_change


class MarketDataService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.cache = CacheService()
        self.db = get_database()

    async def get_quote(self, ticker: str) -> Quote:
        ticker = ticker.upper()
        if self.settings.demo_mode:
            return latest_quote_from_scores(ticker, generate_score_history(ticker))

        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.fast_info
            price = float(info.get("lastPrice") or info.get("regularMarketPrice"))
            previous_close = float(info.get("previousClose") or price)
            payload = {
                "ticker": ticker,
                "company_name": ticker_obj.info.get("shortName", ticker),
                "price": price,
                "previous_close": previous_close,
                "daily_change": round(price - previous_close, 2),
                "daily_change_percent": round(pct_change(price, previous_close), 2),
                "currency": info.get("currency", "USD"),
                "market_state": info.get("marketState", "regular"),
                "as_of": datetime.now(timezone.utc).isoformat(),
                "source": "yfinance",
                "is_stale": False,
            }
            await self.cache.set_cached_document("quotes_cache", f"quote:{ticker}", payload, "yfinance", ttl_minutes=15)
            await self.db["quotes"].update_one({"ticker": ticker}, {"$set": payload}, upsert=True)
            return Quote.model_validate(payload)
        except Exception:
            cached, _ = await self.cache.stale_or_none("quotes_cache", f"quote:{ticker}")
            if cached:
                cached["is_stale"] = True
                return Quote.model_validate(cached)
            return latest_quote_from_scores(ticker, generate_score_history(ticker))

    async def get_price_history(self, ticker: str, period: str = "1y") -> list[dict]:
        ticker = ticker.upper()
        if self.settings.demo_mode:
            rows = [
                {"date": score.date.isoformat(), "close": score.price_close, "open": round(score.price_close * 0.997, 2)}
                for score in generate_score_history(ticker, 365 if period == "1y" else 180)
            ]
            await self._persist_price_history(ticker, rows)
            return rows

        try:
            history = yf.download(ticker, period=period, interval="1d", auto_adjust=False, progress=False)
            rows = []
            for index, row in history.iterrows():
                rows.append({"date": index.date().isoformat(), "close": round(float(row["Close"]), 2), "open": round(float(row["Open"]), 2)})
            if rows:
                await self.cache.set_cached_document("price_cache", f"price:{ticker}:{period}", {"rows": rows}, "yfinance", ttl_minutes=60)
                await self._persist_price_history(ticker, rows)
                return rows
        except Exception:
            pass

        cached, _ = await self.cache.stale_or_none("price_cache", f"price:{ticker}:{period}")
        if cached:
            return cached.get("rows", [])
        rows = [
            {"date": score.date.isoformat(), "close": score.price_close, "open": round(score.price_close * 0.997, 2)}
            for score in generate_score_history(ticker, 365 if period == "1y" else 180)
        ]
        await self._persist_price_history(ticker, rows)
        return rows

    async def _persist_price_history(self, ticker: str, rows: list[dict]) -> None:
        try:
            collection = self.db["price_bars"]
            for row in rows:
                await collection.update_one(
                    {"ticker": ticker, "date": row["date"]},
                    {"$set": {"ticker": ticker, **row}},
                    upsert=True,
                )
        except Exception:
            return
