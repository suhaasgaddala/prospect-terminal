from fastapi import APIRouter, Query

from app.models.api import QuoteResponse
from app.services.market_data_service import MarketDataService

router = APIRouter()


@router.get("/quote", response_model=QuoteResponse)
async def quote(ticker: str = Query(..., min_length=1)) -> QuoteResponse:
    service = MarketDataService()
    return QuoteResponse(quote=await service.get_quote(ticker))
