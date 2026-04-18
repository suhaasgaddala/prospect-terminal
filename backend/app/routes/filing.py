from fastapi import APIRouter, Query

from app.models.api import FilingResponse
from app.services.sec_service import SECService

router = APIRouter()


@router.get("/filing", response_model=FilingResponse)
async def filing(ticker: str = Query(..., min_length=1)) -> FilingResponse:
    service = SECService()
    return FilingResponse(ticker=ticker.upper(), filing=await service.get_filing(ticker))
