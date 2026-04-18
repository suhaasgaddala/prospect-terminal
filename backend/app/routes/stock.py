from datetime import datetime, timezone

from fastapi import APIRouter, Query

from app.models.api import StockResponse
from app.services.macro_service import MacroService
from app.services.market_data_service import MarketDataService
from app.services.news_service import NewsService
from app.services.reddit_service import RedditService
from app.services.scoring_service import ScoringService
from app.services.sec_service import SECService
from app.services.thesis_service import ThesisService
from app.services.x_service import XService

router = APIRouter()


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

    quote = await market_data.get_quote(ticker)
    score_history = await scoring_service.ensure_score_history(ticker, 180)
    latest_score = score_history[-1]
    headlines = await news_service.get_news(ticker)
    social_items = sorted(await x_service.get_posts(ticker) + await reddit_service.get_posts(ticker), key=lambda item: item.created_at, reverse=True)[:6]
    filing = await sec_service.get_filing(ticker)
    macro = await macro_service.get_snapshot()
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
