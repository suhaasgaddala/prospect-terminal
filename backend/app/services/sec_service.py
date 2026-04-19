from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

from bs4 import BeautifulSoup

import httpx

from app.config import get_settings
from app.db import get_database
from app.models.domain import FilingSummary
from app.services.cache_service import CacheService
from app.services.demo_data import generate_filing, generate_score_history
from app.utils.math import clamp
from app.utils.text import compact_whitespace, truncate


class SECService:
    TICKER_LOOKUP_URL = "https://www.sec.gov/files/company_tickers.json"
    RELEVANT_FORMS = {"10-Q", "10-K", "10-Q/A", "10-K/A"}

    CATALYST_THEMES: list[tuple[str, tuple[str, ...], str]] = [
        (
            "demand",
            ("demand", "customer", "orders", "backlog", "pipeline"),
            "Management discussion still points to resilient demand and customer activity.",
        ),
        (
            "growth",
            ("growth", "expand", "opportunity", "increase", "invest"),
            "The filing continues to frame growth opportunities and investment areas constructively.",
        ),
        (
            "margin",
            ("margin", "profitability", "efficiency", "operating leverage", "cost discipline"),
            "Operating leverage and margin commentary remain supportive.",
        ),
        (
            "liquidity",
            ("cash", "liquidity", "balance sheet", "capital allocation", "repurchase"),
            "Balance-sheet language suggests healthy liquidity and flexibility.",
        ),
    ]
    RISK_THEMES: list[tuple[str, tuple[str, ...], str]] = [
        (
            "competition",
            ("competition", "competitive", "pricing pressure", "market share"),
            "Competitive intensity remains a recurring execution risk.",
        ),
        (
            "macro",
            ("inflation", "interest rates", "recession", "macroeconomic", "foreign exchange"),
            "Macro conditions and rates remain a live headwind in the filing.",
        ),
        (
            "operations",
            ("supply chain", "manufacturing", "inventory", "capacity", "disruption"),
            "Operational execution still depends on stable supply and capacity conditions.",
        ),
        (
            "regulatory",
            ("regulation", "regulatory", "litigation", "compliance", "cybersecurity", "privacy"),
            "Regulatory, legal, or cybersecurity language remains meaningful in the risk sections.",
        ),
    ]
    POSITIVE_TERMS: dict[str, float] = {
        "growth": 1.4,
        "demand": 1.3,
        "opportunity": 1.0,
        "liquidity": 1.0,
        "cash": 0.9,
        "margin": 1.2,
        "efficiency": 1.1,
        "invest": 0.8,
        "expansion": 1.1,
        "repurchase": 1.0,
    }
    NEGATIVE_TERMS: dict[str, float] = {
        "risk": 1.0,
        "uncertainty": 1.2,
        "competition": 1.3,
        "inflation": 1.0,
        "litigation": 1.5,
        "cybersecurity": 1.5,
        "disruption": 1.3,
        "debt": 0.8,
        "impairment": 1.7,
        "weakness": 1.1,
        "decline": 1.2,
    }

    def __init__(self) -> None:
        self.settings = get_settings()
        self.cache = CacheService()
        self.db = get_database()

    async def get_filing(self, ticker: str) -> FilingSummary:
        ticker = ticker.upper()
        try:
            cik = await self._ticker_to_cik(ticker)
            if cik:
                filing = await self._fetch_latest_filing(ticker, cik)
                if filing:
                    try:
                        await self.db["filings"].update_one({"ticker": ticker}, {"$set": filing.model_dump(mode="json")}, upsert=True)
                    except Exception:
                        pass
                    return filing
        except Exception:
            pass

        try:
            cached = await self.db["filings"].find_one({"ticker": ticker}, {"_id": 0})
            if cached:
                cached["is_stale"] = True
                return FilingSummary.model_validate(cached)
        except Exception:
            pass
        return generate_filing(ticker, generate_score_history(ticker))

    async def _ticker_to_cik(self, ticker: str) -> str | None:
        cached = await self.cache.get_cached_document("reference_cache", "sec:ticker_lookup")
        payload = cached.get("payload") if cached else None
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
            filing_row = self._select_latest_relevant_filing(payload)
            if not filing_row:
                return None

            accession_number = filing_row["accessionNumber"]
            accession_no_dashes = accession_number.replace("-", "")
            company_name = payload.get("name")
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_no_dashes}/{filing_row['primaryDocument']}"
            filing_text = await self._fetch_filing_text(
                client,
                cik=cik,
                accession_number=accession_number,
                filing_url=filing_url,
            )

        analysis = self._analyze_filing(
            ticker=ticker,
            company_name=company_name,
            form_type=filing_row["form"],
            filing_date=filing_row["filingDate"],
            filing_text=filing_text,
        )

        return FilingSummary(
            ticker=ticker,
            company_name=company_name,
            accession_number=accession_number,
            cik=cik,
            form_type=filing_row["form"],
            filed_at=datetime.fromisoformat(filing_row["filingDate"]).replace(tzinfo=UTC),
            filing_url=filing_url,
            summary=analysis["summary"],
            signal_score=analysis["signal_score"],
            highlights=analysis["highlights"],
            risks=analysis["risks"],
            source="sec",
        )

    def _select_latest_relevant_filing(self, payload: dict[str, Any]) -> dict[str, str] | None:
        recent = payload.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        accession_numbers = recent.get("accessionNumber", [])
        filing_dates = recent.get("filingDate", [])
        primary_docs = recent.get("primaryDocument", [])
        if not forms or not accession_numbers or not filing_dates or not primary_docs:
            return None
        for form, accession_number, filing_date, primary_doc in zip(forms, accession_numbers, filing_dates, primary_docs):
            if form in self.RELEVANT_FORMS:
                return {
                    "form": form,
                    "accessionNumber": accession_number,
                    "filingDate": filing_date,
                    "primaryDocument": primary_doc,
                }
        return None

    async def _fetch_filing_text(
        self,
        client: httpx.AsyncClient,
        *,
        cik: str,
        accession_number: str,
        filing_url: str,
    ) -> str:
        accession_no_dashes = accession_number.replace("-", "")
        txt_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_no_dashes}/{accession_number}.txt"
        for url in (filing_url, txt_url):
            response = await client.get(url)
            if response.status_code >= 400:
                continue
            normalized = self._normalize_filing_text(response.text)
            if normalized:
                return normalized
        return ""

    def _normalize_filing_text(self, raw_text: str) -> str:
        soup = BeautifulSoup(raw_text, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        for tag in soup.find_all():
            tag_name = (tag.name or "").lower()
            if tag_name in {"table", "ix:header"} or tag_name.startswith(
                ("ix:", "xbrli:", "xbrldi:", "ixt:", "dei:", "us-gaap:", "link:", "xlink:")
            ):
                tag.decompose()
                continue
            attrs = getattr(tag, "attrs", {}) or {}
            style = str(attrs.get("style", "")).replace(" ", "").lower()
            if "display:none" in style:
                tag.decompose()
        text = soup.get_text("\n")
        text = text.replace("\r", "\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        markers = [
            "UNITED STATES SECURITIES AND EXCHANGE COMMISSION",
            "FORM 10-Q",
            "FORM 10-K",
            "PART I",
        ]
        upper = text.upper()
        for marker in markers:
            index = upper.find(marker)
            if index > 0:
                text = text[index:]
                break
        return text.strip()

    def _extract_section(self, text: str, start_patterns: list[str], end_patterns: list[str]) -> str:
        upper = text.upper()
        start_index = -1
        for pattern in start_patterns:
            match = re.search(pattern, upper)
            if match:
                start_index = match.start()
                break
        if start_index == -1:
            return ""
        end_index = len(text)
        for pattern in end_patterns:
            match = re.search(pattern, upper[start_index + 1 :])
            if match:
                end_index = start_index + 1 + match.start()
                break
        return text[start_index:end_index][:12000]

    def _extract_theme_points(
        self,
        text: str,
        themes: list[tuple[str, tuple[str, ...], str]],
        *,
        fallback: list[str],
    ) -> list[str]:
        scored: list[tuple[int, str]] = []
        lower = text.lower()
        for _, terms, sentence in themes:
            hits = sum(lower.count(term) for term in terms)
            if hits > 0:
                scored.append((hits, sentence))
        if not scored:
            return fallback[:3]
        scored.sort(key=lambda item: item[0], reverse=True)
        unique_points: list[str] = []
        for _, sentence in scored:
            if sentence not in unique_points:
                unique_points.append(sentence)
            if len(unique_points) == 3:
                break
        return unique_points

    def _weighted_term_score(self, text: str, weights: dict[str, float]) -> float:
        lower = text.lower()
        return sum(lower.count(term) * weight for term, weight in weights.items())

    def _analyze_filing(
        self,
        *,
        ticker: str,
        company_name: str | None,
        form_type: str,
        filing_date: str,
        filing_text: str,
    ) -> dict[str, Any]:
        risk_section = self._extract_section(
            filing_text,
            start_patterns=[r"ITEM\s+1A\.?\s+RISK FACTORS", r"\bRISK FACTORS\b"],
            end_patterns=[r"ITEM\s+1B", r"ITEM\s+2", r"ITEM\s+3", r"UNRESOLVED STAFF COMMENTS"],
        )
        discussion_section = self._extract_section(
            filing_text,
            start_patterns=[
                r"ITEM\s+2\.?\s+MANAGEMENT\S*\s+DISCUSSION",
                r"ITEM\s+7\.?\s+MANAGEMENT\S*\s+DISCUSSION",
                r"MANAGEMENT\S*\s+DISCUSSION AND ANALYSIS",
            ],
            end_patterns=[r"ITEM\s+3", r"ITEM\s+7A", r"ITEM\s+8", r"QUANTITATIVE AND QUALITATIVE DISCLOSURES"],
        )
        analysis_text = "\n".join(section for section in (discussion_section, risk_section) if section).strip() or filing_text

        positive_score = self._weighted_term_score(analysis_text, self.POSITIVE_TERMS)
        negative_score = self._weighted_term_score(analysis_text, self.NEGATIVE_TERMS)
        base_score = 54 if form_type.startswith("10-Q") else 52
        signal_score = round(clamp(base_score + min(14, positive_score * 1.6) - min(18, negative_score * 1.4)), 2)

        highlights = self._extract_theme_points(
            discussion_section or analysis_text,
            self.CATALYST_THEMES,
            fallback=[
                "The filing includes the current management discussion and financial update.",
                "Latest SEC report has been pulled directly from EDGAR.",
                "Signal is based on deterministic keyword analysis of the filing text.",
            ],
        )
        risks = self._extract_theme_points(
            risk_section or analysis_text,
            self.RISK_THEMES,
            fallback=[
                "Risk-factor language remains important to the current filing signal.",
                "Broader macro and execution conditions still need monitoring.",
                "Use the filing score with the broader multi-source score stack.",
            ],
        )

        tone = "constructive" if signal_score >= 58 else "cautious" if signal_score <= 45 else "mixed"
        lead = company_name or ticker
        catalyst_headline = compact_whitespace(highlights[0]).rstrip(".")
        risk_headline = compact_whitespace(risks[0]).rstrip(".")
        summary = truncate(
            f"{lead}'s latest {form_type} filed on {filing_date} reads {tone}. "
            f"Likely catalyst: {catalyst_headline}. Key risk: {risk_headline}.",
            280,
        )

        return {
            "summary": summary,
            "signal_score": signal_score,
            "highlights": highlights,
            "risks": risks,
        }
