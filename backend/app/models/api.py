from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel

from app.models.domain import (
    BacktestMetrics,
    BacktestTrade,
    ContentItem,
    EquityPoint,
    FilingSummary,
    LeaderboardEntry,
    MacroSnapshot,
    Quote,
    ScoreComponents,
    Thesis,
)


class ServiceStatus(BaseModel):
    name: str
    configured: bool
    status: Literal["ok", "missing_config", "error"]


class HealthResponse(BaseModel):
    name: str
    environment: str
    database_connected: bool
    demo_mode: bool
    use_cached_data: bool
    services: list[ServiceStatus]
    server_time: datetime


class QuoteResponse(BaseModel):
    quote: Quote


class StockResponse(BaseModel):
    quote: Quote
    score: float
    components: ScoreComponents
    thesis: Thesis
    filing: FilingSummary
    social_items: list[ContentItem]
    headlines: list[ContentItem]
    macro: MacroSnapshot
    updated_at: datetime


class ScoreHistoryPoint(BaseModel):
    date: date
    overall_score: float
    price_close: float
    components: ScoreComponents


class ScoreHistoryResponse(BaseModel):
    ticker: str
    range: str
    points: list[ScoreHistoryPoint]


class LeaderboardResponse(BaseModel):
    bullish: list[LeaderboardEntry]
    bearish: list[LeaderboardEntry]
    updated_at: datetime


class MacroResponse(BaseModel):
    snapshot: MacroSnapshot


class SocialResponse(BaseModel):
    ticker: str
    items: list[ContentItem]


class NewsResponse(BaseModel):
    ticker: str
    items: list[ContentItem]


class FilingResponse(BaseModel):
    ticker: str
    filing: FilingSummary


class BacktestResponse(BaseModel):
    ticker: str
    strategy: str
    start: date
    end: date
    metrics: BacktestMetrics
    equity_curve: list[EquityPoint]
    trades: list[BacktestTrade]
