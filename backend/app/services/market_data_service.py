from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timezone

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
        try:
            payload = await asyncio.to_thread(self._fetch_quote_live, ticker)
            try:
                await self.cache.set_cached_document("quotes_cache", f"quote:{ticker}", payload, "yfinance", ttl_minutes=15)
            except Exception:
                pass
            try:
                await self.db["quotes"].update_one({"ticker": ticker}, {"$set": payload}, upsert=True)
            except Exception:
                pass
            return Quote.model_validate(payload)
        except Exception:
            try:
                cached, _ = await self.cache.stale_or_none("quotes_cache", f"quote:{ticker}")
                if cached:
                    cached["is_stale"] = True
                    return Quote.model_validate(cached)
            except Exception:
                pass
            return latest_quote_from_scores(ticker, generate_score_history(ticker))

    async def get_price_history(self, ticker: str, period: str = "1y") -> list[dict]:
        ticker = ticker.upper()
        try:
            rows = await asyncio.to_thread(self._fetch_price_history_live, ticker, period)
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

    def _fetch_quote_live(self, ticker: str) -> dict:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.fast_info
        full_info = ticker_obj.info or {}
        price = float(
            info.get("lastPrice")
            or info.get("regularMarketPrice")
            or full_info.get("regularMarketPrice")
            or full_info.get("currentPrice")
        )
        previous_close = float(info.get("previousClose") or price)
        market_timestamp = full_info.get("regularMarketTime")
        as_of = (
            datetime.fromtimestamp(market_timestamp, tz=UTC).isoformat()
            if isinstance(market_timestamp, (int, float))
            else datetime.now(timezone.utc).isoformat()
        )
        return {
            "ticker": ticker,
            "company_name": full_info.get("shortName", ticker),
            "price": price,
            "previous_close": previous_close,
            "daily_change": round(price - previous_close, 2),
            "daily_change_percent": round(pct_change(price, previous_close), 2),
            "currency": info.get("currency", "USD"),
            "market_state": info.get("marketState", "regular"),
            "as_of": as_of,
            "source": "yfinance",
            "is_stale": False,
        }

    def _fetch_price_history_live(self, ticker: str, period: str) -> list[dict]:
        history = yf.download(ticker, period=period, interval="1d", auto_adjust=False, progress=False)
        if getattr(history.columns, "nlevels", 1) > 1:
            close_series = history["Close"].iloc[:, 0]
            open_series = history["Open"].iloc[:, 0]
        else:
            close_series = history["Close"]
            open_series = history["Open"]
        rows = []
        for index in history.index:
            rows.append(
                {
                    "date": index.date().isoformat(),
                    "close": round(float(close_series.loc[index]), 2),
                    "open": round(float(open_series.loc[index]), 2),
                }
            )
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
