from fastapi import APIRouter

from app.models.api import MacroResponse
from app.services.macro_service import MacroService

router = APIRouter()


@router.get("/macro", response_model=MacroResponse)
async def macro() -> MacroResponse:
    service = MacroService()
    return MacroResponse(snapshot=await service.get_snapshot())
