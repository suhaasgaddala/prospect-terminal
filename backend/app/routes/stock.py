import asyncio
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Query

from app.models.api import StockResponse
from app.models.domain import ContentItem, DailyScore, FilingSummary, MacroSnapshot, Quote
from app.services.demo_data import (
    generate_filing,
    generate_macro_history,
    generate_news_items,
    generate_score_history,
    generate_social_items,
    latest_quote_from_scores,
)
from app.services.macro_service import MacroService
from app.services.market_data_service import MarketDataService
from app.services.news_service import NewsService
from app.services.reddit_service import RedditService
from app.services.scoring_service import ScoringService
from app.services.sec_service import SECService
from app.services.thesis_service import ThesisService
from app.services.x_service import XService

router = APIRouter()
logger = logging.getLogger(__name__)

_SCORE_DAYS = 180


def _demo_scores(ticker: str) -> list[DailyScore]:
    return generate_score_history(ticker, _SCORE_DAYS)


def _fallback_quote(ticker: str) -> Quote:
    return latest_quote_from_scores(ticker, _demo_scores(ticker))


def _fallback_news(ticker: str, scores: list[DailyScore]) -> list[ContentItem]:
    return generate_news_items(ticker, scores)


def _fallback_x_posts(ticker: str, scores: list[DailyScore]) -> list[ContentItem]:
    return [item for item in generate_social_items(ticker, scores) if item.source == "x"]


def _fallback_reddit_posts(ticker: str, scores: list[DailyScore]) -> list[ContentItem]:
    return [item for item in generate_social_items(ticker, scores) if item.source == "reddit"]


def _fallback_filing(ticker: str, scores: list[DailyScore]) -> FilingSummary:
    return generate_filing(ticker, scores)


def _fallback_macro() -> MacroSnapshot:
    return generate_macro_history()[-1]


def _apply_live_filing_to_score(score: DailyScore, filing: FilingSummary) -> DailyScore:
    updated = score.model_copy(deep=True)
    updated.components.filings = filing.signal_score
    updated.overall_score = round(
        updated.components.news * 0.25
        + updated.components.x * 0.20
        + updated.components.reddit * 0.15
        + updated.components.filings * 0.20
        + updated.components.macro * 0.20,
        2,
    )
    updated.evidence_summary["filings"] = filing.summary
    return updated


@router.get("/stock", response_model=StockResponse)
async def stock(ticker: str = Query(..., min_length=1)) -> StockResponse:
    ticker = ticker.upper()
    market_data = MarketDataService()
    news_service = NewsService()
    reddit_service = RedditService()
    x_service = XService()
    sec_service = SECService()
    macro_service = MacroService()
    scoring_service = ScoringService()
    thesis_service = ThesisService()

    quote_result, score_result = await asyncio.gather(
        market_data.get_quote(ticker),
        scoring_service.ensure_score_history(ticker, _SCORE_DAYS),
        return_exceptions=True,
    )

    if isinstance(quote_result, Exception):
        logger.warning("stock route: quote failed for %s, using demo quote fallback: %r", ticker, quote_result)
        quote = _fallback_quote(ticker)
    else:
        quote = quote_result

    if isinstance(score_result, Exception):
        logger.warning("stock route: score history failed for %s, using demo score series: %r", ticker, score_result)
        score_history = _demo_scores(ticker)
    else:
        score_history = score_result

    latest_score = score_history[-1]

    opt_news, opt_x, opt_reddit, opt_filing, opt_macro = await asyncio.gather(
        news_service.get_news(ticker),
        x_service.get_posts(ticker),
        reddit_service.get_posts(ticker),
        sec_service.get_filing(ticker),
        macro_service.get_snapshot(),
        return_exceptions=True,
    )

    optional_failures = (opt_news, opt_x, opt_reddit, opt_filing, opt_macro)
    needs_demo_scores = any(isinstance(result, Exception) for result in optional_failures)
    scores_for_fallbacks = _demo_scores(ticker) if needs_demo_scores else None

    if isinstance(opt_news, Exception):
        logger.warning("stock route: news failed for %s, using demo headlines: %r", ticker, opt_news)
        assert scores_for_fallbacks is not None
        headlines = _fallback_news(ticker, scores_for_fallbacks)
    else:
        headlines = opt_news

    if isinstance(opt_x, Exception):
        logger.warning("stock route: X posts failed for %s, using demo X items: %r", ticker, opt_x)
        assert scores_for_fallbacks is not None
        x_items = _fallback_x_posts(ticker, scores_for_fallbacks)
    else:
        x_items = opt_x

    if isinstance(opt_reddit, Exception):
        logger.warning("stock route: Reddit posts failed for %s, using demo Reddit items: %r", ticker, opt_reddit)
        assert scores_for_fallbacks is not None
        reddit_items = _fallback_reddit_posts(ticker, scores_for_fallbacks)
    else:
        reddit_items = opt_reddit

    if isinstance(opt_filing, Exception):
        logger.warning("stock route: filing failed for %s, using demo filing: %r", ticker, opt_filing)
        assert scores_for_fallbacks is not None
        filing = _fallback_filing(ticker, scores_for_fallbacks)
    else:
        filing = opt_filing

    if isinstance(opt_macro, Exception):
        logger.warning("stock route: macro snapshot failed for %s, using demo macro: %r", ticker, opt_macro)
        macro = _fallback_macro()
    else:
        macro = opt_macro

    latest_score = _apply_live_filing_to_score(latest_score, filing)

    social_items = sorted(x_items + reddit_items, key=lambda item: item.created_at, reverse=True)[:6]
    thesis = await thesis_service.get_thesis(ticker, latest_score, headlines, social_items, filing, macro, score_history)

    return StockResponse(
        quote=quote,
        score=latest_score.overall_score,
        components=latest_score.components,
        thesis=thesis,
        filing=filing,
        social_items=social_items,
        headlines=headlines[:5],
        macro=macro,
        updated_at=datetime.now(timezone.utc),
    )
