import asyncio
from datetime import date, timedelta

from app.services.backtest_service import BacktestService


def test_backtest_returns_metrics() -> None:
    service = BacktestService()
    end = date.today()
    start = end - timedelta(days=120)
    result = asyncio.run(service.run_backtest("NVDA", start, end, "threshold_cross"))
    assert result.metrics.trade_count >= 1
    assert len(result.equity_curve) > 20
    assert result.metrics.max_drawdown >= 0
