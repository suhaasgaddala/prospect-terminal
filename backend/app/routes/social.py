from fastapi import APIRouter, Query

from app.models.api import SocialResponse
from app.services.reddit_service import RedditService
from app.services.x_service import XService

router = APIRouter()


@router.get("/social", response_model=SocialResponse)
async def social(ticker: str = Query(..., min_length=1)) -> SocialResponse:
    x_service = XService()
    reddit_service = RedditService()
    x_items = await x_service.get_posts(ticker)
    reddit_items = await reddit_service.get_posts(ticker)
    items = sorted(x_items + reddit_items, key=lambda item: item.created_at, reverse=True)
    return SocialResponse(ticker=ticker.upper(), items=items[:8])
