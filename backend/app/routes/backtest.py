from datetime import date, timedelta

from fastapi import APIRouter, Query

from app.models.api import BacktestResponse
from app.services.backtest_service import BacktestService

router = APIRouter()


@router.get("/backtest", response_model=BacktestResponse)
async def backtest(
    ticker: str = Query(...),
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    strategy: str = Query(default="threshold_cross"),
    threshold: float = Query(default=60),
    exit_threshold: float = Query(default=45),
    momentum_window: int = Query(default=5),
    momentum_delta: float = Query(default=8),
) -> BacktestResponse:
    today = date.today()
    end = end or today
    start = start or (end - timedelta(days=180))
    service = BacktestService()
    return await service.run_backtest(ticker, start, end, strategy, threshold, exit_threshold, momentum_window, momentum_delta)
