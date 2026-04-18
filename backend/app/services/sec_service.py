from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.config import get_settings
from app.db import get_database
from app.models.domain import FilingSummary
from app.services.cache_service import CacheService
from app.services.demo_data import generate_filing, generate_score_history
from app.utils.math import clamp


class SECService:
    TICKER_LOOKUP_URL = "https://www.sec.gov/files/company_tickers.json"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.cache = CacheService()
        self.db = get_database()

    async def get_filing(self, ticker: str) -> FilingSummary:
        ticker = ticker.upper()
        if self.settings.demo_mode:
            return generate_filing(ticker, generate_score_history(ticker))

        try:
            cik = await self._ticker_to_cik(ticker)
            if cik:
                filing = await self._fetch_latest_filing(ticker, cik)
                if filing:
                    await self.db["filings"].update_one({"ticker": ticker}, {"$set": filing.model_dump(mode="json")}, upsert=True)
                    return filing
        except Exception:
            pass

        cached = await self.db["filings"].find_one({"ticker": ticker}, {"_id": 0})
        if cached:
            cached["is_stale"] = True
            return FilingSummary.model_validate(cached)
        return generate_filing(ticker, generate_score_history(ticker))

    async def _ticker_to_cik(self, ticker: str) -> str | None:
        cached, _ = await self.cache.stale_or_none("reference_cache", "sec:ticker_lookup")
        payload = cached
        if payload is None:
            headers = {"User-Agent": self.settings.sec_user_agent}
            async with httpx.AsyncClient(timeout=20, headers=headers) as client:
                response = await client.get(self.TICKER_LOOKUP_URL)
                response.raise_for_status()
                payload = response.json()
            await self.cache.set_cached_document("reference_cache", "sec:ticker_lookup", payload, "sec", ttl_minutes=1440)
        for _, row in payload.items():
            if row.get("ticker") == ticker:
                return str(row.get("cik_str")).zfill(10)
        return None

    async def _fetch_latest_filing(self, ticker: str, cik: str) -> FilingSummary | None:
        headers = {"User-Agent": self.settings.sec_user_agent}
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        async with httpx.AsyncClient(timeout=20, headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()
        recent = payload.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        accession_numbers = recent.get("accessionNumber", [])
        filing_dates = recent.get("filingDate", [])
        primary_docs = recent.get("primaryDocument", [])
        if not forms:
            return None
        form_type = forms[0]
        filing_date = filing_dates[0]
        accession = accession_numbers[0].replace("-", "")
        primary_doc = primary_docs[0]
        filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{primary_doc}"
        signal_score = self._score_form(form_type)
        return FilingSummary(
            ticker=ticker,
            form_type=form_type,
            filed_at=datetime.fromisoformat(filing_date).replace(tzinfo=timezone.utc),
            filing_url=filing_url,
            summary=f"Latest {form_type} filing parsed from SEC submissions feed. Signal score reflects form type and simple risk-language heuristics.",
            signal_score=signal_score,
            highlights=["Filing available in SEC submissions feed.", "Form type mapped to a simple deterministic signal.", "Cached for demo reliability."],
            risks=["Full section-level parsing is limited in v1 live mode.", "Signal may lag nuanced filing context.", "Use with score components, not alone."],
            source="sec",
        )

    def _score_form(self, form_type: str) -> float:
        mapping = {"8-K": 58, "10-Q": 55, "10-K": 53, "S-3": 40, "424B5": 35}
        return round(clamp(mapping.get(form_type, 50)), 2)
