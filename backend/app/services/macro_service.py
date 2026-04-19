from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import httpx
import yfinance as yf

from app.config import get_settings
from app.db import get_database
from app.models.domain import MacroFactor, MacroSnapshot
from app.services.cache_service import CacheService
from app.services.demo_data import generate_macro_history
from app.utils.math import clamp


class MacroService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.cache = CacheService()
        self.db = get_database()

    async def get_snapshot(self) -> MacroSnapshot:
        if self.settings.demo_mode:
            return generate_macro_history()[-1]

        try:
            snapshot = await self._build_live_snapshot()
            await self.db["macro_snapshots"].update_one({"key": "latest"}, {"$set": snapshot.model_dump(mode="json")}, upsert=True)
            await self.cache.set_cached_document("macro_cache", "latest", snapshot.model_dump(mode="json"), "macro", ttl_minutes=120)
            return snapshot
        except Exception:
            cached, _ = await self.cache.stale_or_none("macro_cache", "latest")
            if cached:
                cached["is_stale"] = True
                return MacroSnapshot.model_validate(cached)
            return generate_macro_history()[-1]

    async def get_history(self, start_date: date, end_date: date) -> list[MacroSnapshot]:
        try:
            history = await self._build_live_history(start_date, end_date)
            if history:
                await self._persist_history(history)
                return history
        except Exception:
            pass

        try:
            cursor = self.db["macro_snapshots"].find(
                {
                    "date": {
                        "$gte": start_date.isoformat(),
                        "$lte": end_date.isoformat(),
                    }
                },
                {"_id": 0},
            ).sort("date", 1)
            cached = [self._snapshot_from_document(row) async for row in cursor]
            if cached:
                return cached
        except Exception:
            pass

        demo = generate_macro_history((end_date - start_date).days + 15)
        return [snapshot for snapshot in demo if start_date <= snapshot.as_of.date() <= end_date]

    async def _build_live_snapshot(self) -> MacroSnapshot:
        tickers = yf.download("SPY QQQ ^VIX ^TNX", period="10d", interval="1d", auto_adjust=False, progress=False)
        close = tickers["Close"]
        spy = close["SPY"].dropna()
        qqq = close["QQQ"].dropna()
        vix = close["^VIX"].dropna()
        tnx = close["^TNX"].dropna() / 10
        spy_delta = float((spy.iloc[-1] / spy.iloc[-5] - 1) * 100) if len(spy) >= 5 else 0.0
        qqq_delta = float((qqq.iloc[-1] / qqq.iloc[-5] - 1) * 100) if len(qqq) >= 5 else 0.0
        vix_value = float(vix.iloc[-1]) if len(vix) else 19.0
        tnx_value = float(tnx.iloc[-1]) if len(tnx) else 4.1
        cpi_delta = await self._fetch_fred_delta("CPIAUCSL")
        score = clamp(60 + spy_delta * 3 + qqq_delta * 3 - max(vix_value - 18, 0) * 2.5 - max(tnx_value - 4.0, 0) * 5 - max(cpi_delta, 0) * 0.4)
        regime = "risk-on" if score >= 60 else "mixed" if score >= 45 else "risk-off"
        return MacroSnapshot(
            as_of=datetime.now(timezone.utc),
            score=round(score, 2),
            regime=regime,
            summary="Live macro snapshot combines index momentum, volatility, rates, and inflation trend.",
            factors=[
                MacroFactor(name="SPY Trend", value=round(float(spy.iloc[-1]), 2), delta=round(spy_delta, 2), signal="bullish" if spy_delta > 1 else "bearish" if spy_delta < -1 else "neutral", summary="Five-day broad market move."),
                MacroFactor(name="QQQ Momentum", value=round(float(qqq.iloc[-1]), 2), delta=round(qqq_delta, 2), signal="bullish" if qqq_delta > 1 else "bearish" if qqq_delta < -1 else "neutral", summary="Five-day growth leadership move."),
                MacroFactor(name="VIX", value=round(vix_value, 2), delta=round(float(vix.iloc[-1] - vix.iloc[-2]), 2) if len(vix) >= 2 else 0.0, signal="bullish" if vix_value < 18 else "bearish" if vix_value > 23 else "neutral", summary="Implied volatility regime."),
                MacroFactor(name="10Y Yield", value=round(tnx_value, 2), delta=round(float(tnx.iloc[-1] - tnx.iloc[-2]), 2) if len(tnx) >= 2 else 0.0, signal="bearish" if tnx_value > 4.3 else "bullish" if tnx_value < 3.9 else "neutral", summary="US 10Y Treasury yield."),
            ],
        )

    async def _build_live_history(self, start_date: date, end_date: date) -> list[MacroSnapshot]:
        fetch_start = start_date - timedelta(days=10)
        fetch_end = end_date + timedelta(days=1)
        tickers = yf.download(
            "SPY QQQ ^VIX ^TNX",
            start=fetch_start.isoformat(),
            end=fetch_end.isoformat(),
            interval="1d",
            auto_adjust=False,
            progress=False,
        )
        if tickers.empty:
            return []

        close = tickers["Close"]
        spy = close["SPY"].dropna()
        qqq = close["QQQ"].dropna()
        vix = close["^VIX"].dropna()
        tnx = (close["^TNX"].dropna() / 10).round(4)
        common_dates = sorted(set(spy.index) & set(qqq.index) & set(vix.index) & set(tnx.index))
        history: list[MacroSnapshot] = []
        for index, ts in enumerate(common_dates):
            day = ts.date()
            if day < start_date or day > end_date:
                continue
            lookback_index = max(0, index - 4)
            lookback_date = common_dates[lookback_index]
            spy_delta = float((spy.loc[ts] / spy.loc[lookback_date] - 1) * 100) if spy.loc[lookback_date] else 0.0
            qqq_delta = float((qqq.loc[ts] / qqq.loc[lookback_date] - 1) * 100) if qqq.loc[lookback_date] else 0.0
            vix_value = float(vix.loc[ts])
            vix_delta = float(vix.loc[ts] - vix.loc[common_dates[index - 1]]) if index > 0 else 0.0
            tnx_value = float(tnx.loc[ts])
            tnx_delta = float(tnx.loc[ts] - tnx.loc[common_dates[index - 1]]) if index > 0 else 0.0
            score = clamp(60 + spy_delta * 3 + qqq_delta * 3 - max(vix_value - 18, 0) * 2.5 - max(tnx_value - 4.0, 0) * 5)
            regime = "risk-on" if score >= 60 else "mixed" if score >= 45 else "risk-off"
            history.append(
                MacroSnapshot(
                    as_of=datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc),
                    score=round(score, 2),
                    regime=regime,
                    summary="Historical macro context from SPY, QQQ, VIX, and 10Y yield at that date.",
                    factors=[
                        MacroFactor(name="SPY Trend", value=round(float(spy.loc[ts]), 2), delta=round(spy_delta, 2), signal="bullish" if spy_delta > 1 else "bearish" if spy_delta < -1 else "neutral", summary="Trailing broad market move as of that session."),
                        MacroFactor(name="QQQ Momentum", value=round(float(qqq.loc[ts]), 2), delta=round(qqq_delta, 2), signal="bullish" if qqq_delta > 1 else "bearish" if qqq_delta < -1 else "neutral", summary="Trailing growth leadership move as of that session."),
                        MacroFactor(name="VIX", value=round(vix_value, 2), delta=round(vix_delta, 2), signal="bullish" if vix_value < 18 else "bearish" if vix_value > 23 else "neutral", summary="Implied volatility regime as of that session."),
                        MacroFactor(name="10Y Yield", value=round(tnx_value, 2), delta=round(tnx_delta, 2), signal="bearish" if tnx_value > 4.3 else "bullish" if tnx_value < 3.9 else "neutral", summary="US 10Y Treasury yield as of that session."),
                    ],
                )
            )
        return history

    async def _persist_history(self, history: list[MacroSnapshot]) -> None:
        try:
            collection = self.db["macro_snapshots"]
            for snapshot in history:
                payload = snapshot.model_dump(mode="json")
                await collection.update_one(
                    {"date": snapshot.as_of.date().isoformat()},
                    {"$set": {"date": snapshot.as_of.date().isoformat(), **payload}},
                    upsert=True,
                )
        except Exception:
            return

    def _snapshot_from_document(self, payload: dict) -> MacroSnapshot:
        payload = dict(payload)
        payload.pop("date", None)
        return MacroSnapshot.model_validate(payload)

    async def _fetch_fred_delta(self, series_id: str) -> float:
        if not self.settings.fred_api_key:
            return 0.0
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {"series_id": series_id, "api_key": self.settings.fred_api_key, "file_type": "json", "limit": 2, "sort_order": "desc"}
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
        observations = payload.get("observations", [])
        if len(observations) < 2:
            return 0.0
        latest = float(observations[0]["value"])
        previous = float(observations[1]["value"])
        return latest - previous
