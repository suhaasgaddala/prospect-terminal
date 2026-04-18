from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl


SentimentLabel = Literal["bullish", "bearish", "neutral"]
ContentSource = Literal["x", "reddit", "news"]
ThesisRating = Literal["bullish", "neutral", "bearish"]
StrategyName = Literal["threshold_cross", "score_momentum"]


class Engagement(BaseModel):
    likes: int = 0
    comments: int = 0
    shares: int = 0
    score: int = 0


class Sentiment(BaseModel):
    label: SentimentLabel
    score: float


class ContentItem(BaseModel):
    source: ContentSource
    ticker: str
    text: str
    author: str
    url: str
    created_at: datetime
    engagement: Engagement
    sentiment: Sentiment
    title: Optional[str] = None
    published_at: Optional[datetime] = None


class Quote(BaseModel):
    ticker: str
    company_name: str
    price: float
    previous_close: float
    daily_change: float
    daily_change_percent: float
    currency: str = "USD"
    market_state: str = "regular"
    as_of: datetime
    source: str
    is_stale: bool = False


class FilingSummary(BaseModel):
    ticker: str
    form_type: str
    filed_at: datetime
    filing_url: str
    summary: str
    signal_score: float = Field(ge=0, le=100)
    highlights: list[str]
    risks: list[str]
    source: str = "sec"
    is_stale: bool = False


class MacroFactor(BaseModel):
    name: str
    value: float
    delta: float
    signal: SentimentLabel
    summary: str


class MacroSnapshot(BaseModel):
    as_of: datetime
    score: float = Field(ge=0, le=100)
    regime: str
    summary: str
    factors: list[MacroFactor]
    is_stale: bool = False


class ScoreComponents(BaseModel):
    news: float = Field(ge=0, le=100)
    x: float = Field(ge=0, le=100)
    reddit: float = Field(ge=0, le=100)
    filings: float = Field(ge=0, le=100)
    macro: float = Field(ge=0, le=100)


class DailyScore(BaseModel):
    ticker: str
    date: date
    overall_score: float = Field(ge=0, le=100)
    components: ScoreComponents
    evidence_summary: dict[str, str]
    price_close: float


class Thesis(BaseModel):
    ticker: str
    generated_at: datetime
    rating: ThesisRating
    catalysts: list[str]
    risks: list[str]
    summary: str
    model: str
    is_fallback: bool = False


class BacktestTrade(BaseModel):
    entry_date: date
    exit_date: Optional[date] = None
    entry_price: float
    exit_price: Optional[float] = None
    return_pct: Optional[float] = None
    outcome: Optional[Literal["win", "loss", "open"]] = None


class EquityPoint(BaseModel):
    date: date
    strategy_equity: float
    benchmark_equity: float
    score: float
    price: float
    signal: Literal["buy", "sell", "hold"]


class BacktestMetrics(BaseModel):
    total_return: float
    benchmark_return: float
    trade_count: int
    win_rate: float
    max_drawdown: float


class LeaderboardEntry(BaseModel):
    ticker: str
    company_name: str
    price: float
    daily_change_percent: float
    overall_score: float
    thesis_rating: ThesisRating

