from __future__ import annotations

from datetime import datetime, timezone

from openai import AsyncOpenAI

from app.config import get_settings
from app.db import get_database
from app.models.domain import ContentItem, DailyScore, FilingSummary, MacroSnapshot, Thesis
from app.services.demo_data import generate_thesis


class ThesisService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.db = get_database()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key) if self.settings.openai_api_key else None

    async def get_thesis(
        self,
        ticker: str,
        score: DailyScore,
        headlines: list[ContentItem],
        social_items: list[ContentItem],
        filing: FilingSummary,
        macro: MacroSnapshot,
        history: list[DailyScore],
    ) -> Thesis:
        ticker = ticker.upper()
        try:
            cached = await self.db["theses"].find_one({"ticker": ticker}, {"_id": 0})
            if cached:
                thesis = Thesis.model_validate(cached)
                if thesis.generated_at.date() == datetime.now(timezone.utc).date():
                    return thesis
        except Exception:
            cached = None

        thesis = await self._generate_llm_thesis(ticker, score, headlines, social_items, filing, macro, history)
        if thesis is None:
            thesis = generate_thesis(ticker, history)
        try:
            await self.db["theses"].update_one({"ticker": ticker}, {"$set": thesis.model_dump(mode="json")}, upsert=True)
        except Exception:
            pass
        return thesis

    async def _generate_llm_thesis(
        self,
        ticker: str,
        score: DailyScore,
        headlines: list[ContentItem],
        social_items: list[ContentItem],
        filing: FilingSummary,
        macro: MacroSnapshot,
        history: list[DailyScore],
    ) -> Thesis | None:
        if self.client is None:
            return None
        trend = round(score.overall_score - history[-6].overall_score, 2) if len(history) >= 6 else 0.0
        prompt = f"""
You are writing a concise fintech investment thesis card.
Return JSON with keys: rating, catalysts, risks, summary.
Use rating one of bullish, neutral, bearish.
Ticker: {ticker}
Overall score: {score.overall_score}
Components: {score.components.model_dump()}
Score trend over five sessions: {trend}
Headlines: {[item.text for item in headlines[:3]]}
Social: {[item.text for item in social_items[:3]]}
Filing summary: {filing.summary}
Macro: {macro.summary}
"""
        try:
            response = await self.client.responses.create(
                model=self.settings.openai_model,
                input=prompt,
                temperature=0.3,
                max_output_tokens=300,
            )
            text = response.output_text
            import json

            payload = json.loads(text)
            return Thesis(
                ticker=ticker,
                generated_at=datetime.now(timezone.utc),
                rating=payload["rating"],
                catalysts=payload["catalysts"][:3],
                risks=payload["risks"][:3],
                summary=payload["summary"],
                model=self.settings.openai_model,
                is_fallback=False,
            )
        except Exception:
            return None
