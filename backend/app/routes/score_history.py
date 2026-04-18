from fastapi import APIRouter, Query

from app.models.api import ScoreHistoryPoint, ScoreHistoryResponse
from app.services.scoring_service import ScoringService
from app.utils.dates import range_to_days

router = APIRouter()


@router.get("/score-history", response_model=ScoreHistoryResponse)
async def score_history(ticker: str = Query(...), range: str = Query("3M")) -> ScoreHistoryResponse:
    days = range_to_days(range)
    service = ScoringService()
    scores = await service.ensure_score_history(ticker, days)
    points = [
        ScoreHistoryPoint(
            date=score.date,
            overall_score=score.overall_score,
            price_close=score.price_close,
            components=score.components,
        )
        for score in scores[-days:]
    ]
    return ScoreHistoryResponse(ticker=ticker.upper(), range=range, points=points)
