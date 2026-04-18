from fastapi import APIRouter, Query

from app.models.api import NewsResponse
from app.services.news_service import NewsService

router = APIRouter()


@router.get("/news", response_model=NewsResponse)
async def news(ticker: str = Query(..., min_length=1)) -> NewsResponse:
    service = NewsService()
    return NewsResponse(ticker=ticker.upper(), items=await service.get_news(ticker))
