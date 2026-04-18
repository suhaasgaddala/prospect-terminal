from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.domain import ScoreComponents


class CachedDocument(BaseModel):
    key: str
    source: str
    payload: dict[str, Any]
    fetched_at: datetime
    expires_at: datetime


class DailyScoreDocument(BaseModel):
    ticker: str
    date: date
    overall_score: float
    components: ScoreComponents
    evidence_summary: dict[str, str]
    price_close: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    quote_snapshot: Optional[dict[str, Any]] = None
