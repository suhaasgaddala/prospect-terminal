from __future__ import annotations

import math
from datetime import date, datetime, time, timedelta, timezone
from typing import Iterable

from app.config import get_settings
from app.models.domain import (
    ContentItem,
    DailyScore,
    Engagement,
    FilingSummary,
    MacroFactor,
    MacroSnapshot,
    Quote,
    ScoreComponents,
    Sentiment,
    Thesis,
)
from app.utils.math import clamp, pct_change

COMPANY_NAMES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "NVDA": "NVIDIA Corporation",
    "TSLA": "Tesla, Inc.",
    "AMD": "Advanced Micro Devices, Inc.",
    "META": "Meta Platforms, Inc.",
    "AMZN": "Amazon.com, Inc.",
    "GOOGL": "Alphabet Inc.",
    "PLTR": "Palantir Technologies Inc.",
    "NFLX": "Netflix, Inc.",
    "JPM": "JPMorgan Chase & Co.",
    "SMCI": "Super Micro Computer, Inc.",
}

BASE_SCORES = {
    "NVDA": 76,
    "PLTR": 72,
    "MSFT": 68,
    "META": 64,
    "AMD": 61,
    "AAPL": 58,
    "AMZN": 56,
    "GOOGL": 54,
    "JPM": 52,
    "NFLX": 49,
    "TSLA": 43,
    "SMCI": 39,
}

SOCIAL_SNIPPETS = {
    "bullish": [
        "AI demand checks continue to strengthen and channel commentary is turning more constructive.",
        "Management execution keeps showing up in margins and product cadence.",
        "Flows are rotating back into quality growth and this name is screening well on sentiment.",
    ],
    "bearish": [
        "Multiple threads are calling out valuation stretch and fading momentum.",
        "Traders are worried the recent rally got ahead of fundamentals.",
        "Risk chatter is picking up around competition and a tougher macro tape.",
    ],
    "neutral": [
        "The setup looks mixed with solid demand but more muted upside from here.",
        "Discussion is balanced between execution strength and valuation caution.",
        "There is interest in the name, but conviction still looks selective.",
    ],
}


def _ticker_seed(ticker: str) -> int:
    return sum(ord(char) for char in ticker)


def _utc_datetime(day: date, hour: int = 20) -> datetime:
    return datetime.combine(day, time(hour=hour, tzinfo=timezone.utc))


def _score_components(ticker: str, day_offset: int, macro_score: float) -> ScoreComponents:
    seed = _ticker_seed(ticker)
    base = BASE_SCORES.get(ticker, 55)
    swing = math.sin((day_offset + seed) / 8) * 8
    x_score = clamp(base + swing + math.cos(day_offset / 5) * 3)
    reddit_score = clamp(base + math.sin(day_offset / 6 + seed / 10) * 9)
    news_score = clamp(base + math.cos(day_offset / 7 + seed / 12) * 7)
    filings_score = clamp(base + math.sin(day_offset / 13 + seed / 15) * 6)
    return ScoreComponents(
        news=round(news_score, 2),
        x=round(x_score, 2),
        reddit=round(reddit_score, 2),
        filings=round(filings_score, 2),
        macro=round(macro_score, 2),
    )


def generate_macro_history(days: int = 180) -> list[MacroSnapshot]:
    today = datetime.now(timezone.utc).date()
    snapshots: list[MacroSnapshot] = []
    for offset in range(days):
        day = today - timedelta(days=(days - offset - 1))
        vix = 19 + math.sin(offset / 12) * 4
        tnx = 4.1 + math.cos(offset / 14) * 0.35
        spy_momo = 0.4 + math.sin(offset / 18) * 0.8
        qqq_momo = 0.7 + math.cos(offset / 16) * 1.0
        raw_score = 62 + spy_momo * 10 + qqq_momo * 8 - (vix - 19) * 3 - (tnx - 4.0) * 4
        score = clamp(raw_score)
        regime = "risk-on" if score >= 60 else "mixed" if score >= 45 else "risk-off"
        factors = [
            MacroFactor(
                name="SPY Trend",
                value=round(spy_momo, 2),
                delta=round(spy_momo / 4, 2),
                signal="bullish" if spy_momo > 0.3 else "bearish" if spy_momo < -0.3 else "neutral",
                summary="Broad equities remain constructive." if spy_momo > 0.3 else "Broad equity tape is fading.",
            ),
            MacroFactor(
                name="QQQ Momentum",
                value=round(qqq_momo, 2),
                delta=round(qqq_momo / 5, 2),
                signal="bullish" if qqq_momo > 0.4 else "bearish" if qqq_momo < -0.2 else "neutral",
                summary="Growth leadership is helping AI and software." if qqq_momo > 0.4 else "Growth leadership is losing steam.",
            ),
            MacroFactor(
                name="VIX",
                value=round(vix, 2),
                delta=round(math.sin(offset / 12) * 0.7, 2),
                signal="bullish" if vix < 18 else "bearish" if vix > 23 else "neutral",
                summary="Volatility is contained." if vix < 18 else "Volatility is elevated." if vix > 23 else "Volatility is manageable.",
            ),
            MacroFactor(
                name="10Y Yield",
                value=round(tnx, 2),
                delta=round(math.cos(offset / 14) * 0.06, 2),
                signal="bearish" if tnx > 4.35 else "bullish" if tnx < 3.9 else "neutral",
                summary="Rates are easing the duration headwind." if tnx < 3.9 else "Rates are pressuring duration assets." if tnx > 4.35 else "Rates are stable.",
            ),
        ]
        snapshots.append(
            MacroSnapshot(
                as_of=_utc_datetime(day),
                score=round(score, 2),
                regime=regime,
                summary="Macro backdrop favors selective growth." if regime == "risk-on" else "Macro setup is mixed." if regime == "mixed" else "Macro backdrop is defensive.",
                factors=factors,
            )
        )
    return snapshots


def generate_score_history(ticker: str, days: int = 180) -> list[DailyScore]:
    today = datetime.now(timezone.utc).date()
    macro_history = generate_macro_history(days)
    base_price = {
        "NVDA": 892,
        "PLTR": 28,
        "MSFT": 421,
        "META": 503,
        "AMD": 171,
        "AAPL": 194,
        "AMZN": 183,
        "GOOGL": 165,
        "JPM": 197,
        "NFLX": 612,
        "TSLA": 174,
        "SMCI": 831,
    }.get(ticker, 120)
    seed = _ticker_seed(ticker)
    price = base_price
    scores: list[DailyScore] = []
    for offset in range(days):
        day = today - timedelta(days=(days - offset - 1))
        macro_score = macro_history[offset].score
        components = _score_components(ticker, offset, macro_score)
        overall = round(
            components.news * 0.25
            + components.x * 0.20
            + components.reddit * 0.15
            + components.filings * 0.20
            + components.macro * 0.20,
            2,
        )
        daily_drift = ((overall - 50) / 50) * 0.011 + math.sin((offset + seed) / 10) * 0.004
        price = round(max(5, price * (1 + daily_drift)), 2)
        scores.append(
            DailyScore(
                ticker=ticker,
                date=day,
                overall_score=overall,
                components=components,
                evidence_summary={
                    "news": "Headline tone stayed constructive with AI and product-cycle mentions leading coverage."
                    if components.news >= 55
                    else "Headlines skewed cautious with valuation and demand normalization concerns.",
                    "x": "X sentiment is engagement-weighted and leaning positive."
                    if components.x >= 55
                    else "X sentiment softened as traders focused on execution risk.",
                    "reddit": "Reddit threads leaned bullish on momentum and retail participation."
                    if components.reddit >= 55
                    else "Reddit discussion cooled with more mixed retail conviction.",
                    "filings": "Recent filings highlighted manageable risk language and constructive business commentary."
                    if components.filings >= 55
                    else "Recent filing language emphasized caution around margins, competition, or capital needs.",
                    "macro": macro_history[offset].summary,
                },
                price_close=price,
            )
        )
    return scores


def latest_quote_from_scores(ticker: str, scores: list[DailyScore]) -> Quote:
    company_name = COMPANY_NAMES.get(ticker, ticker)
    latest = scores[-1]
    previous = scores[-2] if len(scores) > 1 else latest
    daily_change = round(latest.price_close - previous.price_close, 2)
    return Quote(
        ticker=ticker,
        company_name=company_name,
        price=latest.price_close,
        previous_close=previous.price_close,
        daily_change=daily_change,
        daily_change_percent=round(pct_change(latest.price_close, previous.price_close), 2),
        as_of=_utc_datetime(latest.date, hour=21),
        source="demo_seed",
    )


def _sentiment_from_score(score: float) -> Sentiment:
    if score >= 57:
        label = "bullish"
    elif score <= 43:
        label = "bearish"
    else:
        label = "neutral"
    normalized = round((score - 50) / 50, 3)
    return Sentiment(label=label, score=normalized)


def generate_social_items(ticker: str, scores: list[DailyScore]) -> list[ContentItem]:
    latest = scores[-1]
    items: list[ContentItem] = []
    score_buckets = [
        ("x", latest.components.x),
        ("reddit", latest.components.reddit),
        ("x", latest.components.x - 5),
        ("reddit", latest.components.reddit + 3),
    ]
    for index, (source, score) in enumerate(score_buckets):
        label = _sentiment_from_score(score).label
        snippet_pool = SOCIAL_SNIPPETS[label]
        text = snippet_pool[index % len(snippet_pool)]
        items.append(
            ContentItem(
                source=source,
                ticker=ticker,
                text=f"{ticker}: {text}",
                author=f"{source}_alpha_{index + 1}",
                url=f"https://example.com/{source}/{ticker.lower()}/{index + 1}",
                created_at=_utc_datetime(latest.date - timedelta(days=index), hour=15 + index),
                engagement=Engagement(
                    likes=90 + (index * 13),
                    comments=18 + (index * 5),
                    shares=12 + (index * 4),
                    score=140 + (index * 25),
                ),
                sentiment=_sentiment_from_score(score),
            )
        )
    return items


def generate_news_items(ticker: str, scores: list[DailyScore]) -> list[ContentItem]:
    latest = scores[-1]
    themes = [
        "analysts highlight durable demand and improving operating leverage",
        "investors weigh valuation against a still-constructive product cycle",
        "new channel checks reinforce debate around next-quarter upside",
    ]
    items: list[ContentItem] = []
    for index, theme in enumerate(themes):
        score = latest.components.news - index * 3 + 2
        items.append(
            ContentItem(
                source="news",
                ticker=ticker,
                title=f"{COMPANY_NAMES.get(ticker, ticker)} outlook update {index + 1}",
                text=f"{COMPANY_NAMES.get(ticker, ticker)} {theme}.",
                author=["Bloomberg", "Reuters", "MarketWatch"][index % 3],
                url=f"https://news.example.com/{ticker.lower()}/{index + 1}",
                created_at=_utc_datetime(latest.date - timedelta(days=index), hour=11),
                published_at=_utc_datetime(latest.date - timedelta(days=index), hour=11),
                engagement=Engagement(score=0),
                sentiment=_sentiment_from_score(score),
            )
        )
    return items


def generate_filing(ticker: str, scores: list[DailyScore]) -> FilingSummary:
    latest = scores[-1]
    filing_score = latest.components.filings
    highlights = [
        "Management commentary remained constructive on demand visibility.",
        "Risk disclosures stayed stable relative to the prior filing.",
        "Capital allocation language did not introduce major new concerns.",
    ]
    risks = [
        "Guidance could still tighten if macro demand softens.",
        "Margin execution remains sensitive to mix and pricing.",
        "Competitive pressure may intensify in core segments.",
    ]
    return FilingSummary(
        ticker=ticker,
        company_name=COMPANY_NAMES.get(ticker, ticker),
        accession_number=f"0000000000-00-{_ticker_seed(ticker):06d}",
        cik=str(_ticker_seed(ticker)).zfill(10),
        form_type="10-Q",
        filed_at=_utc_datetime(latest.date - timedelta(days=5), hour=13),
        filing_url=f"https://www.sec.gov/ixviewer/ix.html?doc=/Archives/{ticker.lower()}-latest.htm",
        summary=f"The latest filing for {ticker} reads mildly {'constructive' if filing_score >= 55 else 'cautious'}, with language that aligns with the current score profile.",
        signal_score=round(filing_score, 2),
        highlights=highlights,
        risks=risks,
    )


def generate_thesis(ticker: str, scores: list[DailyScore]) -> Thesis:
    latest = scores[-1]
    trend = latest.overall_score - scores[-6].overall_score if len(scores) >= 6 else 0
    rating = "bullish" if latest.overall_score >= 60 else "bearish" if latest.overall_score <= 45 else "neutral"
    catalysts = [
        "Social sentiment remains supportive across higher-engagement discussions.",
        "Headline tone is reinforcing the current score regime.",
        "Macro conditions still favor liquid growth leaders."
        if latest.components.macro >= 55
        else "Macro pressure is easing enough to keep downside contained.",
    ]
    risks = [
        "A sharp drop in score momentum would weaken the current setup.",
        "Macro volatility could compress valuation appetite quickly.",
        "Filing language or guidance revisions could shift the signal lower.",
    ]
    direction = "improving" if trend > 2 else "softening" if trend < -2 else "stable"
    summary = f"{ticker} screens {rating} with an overall score of {latest.overall_score:.0f}/100. The recent signal trend is {direction}, led by social tone, filing signal, and the broader macro backdrop."
    return Thesis(
        ticker=ticker,
        generated_at=datetime.now(timezone.utc),
        rating=rating,
        catalysts=catalysts,
        risks=risks,
        summary=summary,
        model="deterministic-demo",
        is_fallback=True,
    )


def all_demo_tickers() -> Iterable[str]:
    return get_settings().demo_tickers
