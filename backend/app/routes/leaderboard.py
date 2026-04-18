from fastapi import APIRouter

from app.models.api import LeaderboardResponse
from app.services.leaderboard_service import LeaderboardService

router = APIRouter()


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def leaderboard() -> LeaderboardResponse:
    service = LeaderboardService()
    return await service.get_leaderboard()
