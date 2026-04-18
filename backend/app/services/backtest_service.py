from __future__ import annotations

from datetime import date

from app.models.api import BacktestResponse
from app.models.domain import BacktestMetrics, BacktestTrade, DailyScore, EquityPoint
from app.services.scoring_service import ScoringService
from app.utils.math import max_drawdown


class BacktestService:
    def __init__(self) -> None:
        self.scoring_service = ScoringService()
        self.transaction_cost = 0.001

    async def run_backtest(
        self,
        ticker: str,
        start: date,
        end: date,
        strategy_name: str,
        threshold: float = 60,
        exit_threshold: float = 45,
        momentum_window: int = 5,
        momentum_delta: float = 8,
    ) -> BacktestResponse:
        history = await self.scoring_service.ensure_score_history(ticker, 365)
        filtered = [row for row in history if start <= row.date <= end]
        if len(filtered) < 2:
            filtered = history[-90:]
        equity_curve, trades = self._simulate(filtered, strategy_name, threshold, exit_threshold, momentum_window, momentum_delta)
        strategy_values = [point.strategy_equity for point in equity_curve] or [1.0]
        benchmark_values = [point.benchmark_equity for point in equity_curve] or [1.0]
        closed_trades = [trade for trade in trades if trade.return_pct is not None]
        wins = [trade for trade in closed_trades if (trade.return_pct or 0) > 0]
        metrics = BacktestMetrics(
            total_return=round((strategy_values[-1] - 1) * 100, 2),
            benchmark_return=round((benchmark_values[-1] - 1) * 100, 2),
            trade_count=len(trades),
            win_rate=round((len(wins) / len(closed_trades)) * 100, 2) if closed_trades else 0.0,
            max_drawdown=max_drawdown(strategy_values),
        )
        return BacktestResponse(
            ticker=ticker.upper(),
            strategy=strategy_name,
            start=filtered[0].date,
            end=filtered[-1].date,
            metrics=metrics,
            equity_curve=equity_curve,
            trades=trades,
        )

    def _simulate(
        self,
        history: list[DailyScore],
        strategy_name: str,
        threshold: float,
        exit_threshold: float,
        momentum_window: int,
        momentum_delta: float,
    ) -> tuple[list[EquityPoint], list[BacktestTrade]]:
        in_position = False
        strategy_equity = 1.0
        benchmark_equity = 1.0
        entry_price = history[0].price_close
        benchmark_start = history[0].price_close
        open_trade: BacktestTrade | None = None
        trades: list[BacktestTrade] = []
        curve: list[EquityPoint] = []

        for index, row in enumerate(history):
            prev = history[index - 1] if index > 0 else row
            daily_return = (row.price_close / prev.price_close - 1) if prev.price_close else 0.0
            signal = self._signal(history, index, strategy_name, threshold, exit_threshold, momentum_window, momentum_delta, in_position)
            if signal == "buy" and not in_position:
                in_position = True
                strategy_equity *= 1 - self.transaction_cost
                entry_price = row.price_close
                open_trade = BacktestTrade(entry_date=row.date, entry_price=entry_price, outcome="open")
            elif signal == "sell" and in_position:
                in_position = False
                strategy_equity *= 1 - self.transaction_cost
                if open_trade:
                    open_trade.exit_date = row.date
                    open_trade.exit_price = row.price_close
                    open_trade.return_pct = round(((row.price_close / open_trade.entry_price) - 1) * 100 - (self.transaction_cost * 200), 2)
                    open_trade.outcome = "win" if (open_trade.return_pct or 0) > 0 else "loss"
                    trades.append(open_trade)
                    open_trade = None
            if in_position:
                strategy_equity *= 1 + daily_return
            benchmark_equity = row.price_close / benchmark_start if benchmark_start else 1.0
            curve.append(
                EquityPoint(
                    date=row.date,
                    strategy_equity=round(strategy_equity, 4),
                    benchmark_equity=round(benchmark_equity, 4),
                    score=row.overall_score,
                    price=row.price_close,
                    signal=signal,
                )
            )

        if open_trade:
            final = history[-1]
            open_trade.exit_date = final.date
            open_trade.exit_price = final.price_close
            open_trade.return_pct = round(((final.price_close / open_trade.entry_price) - 1) * 100 - (self.transaction_cost * 200), 2)
            open_trade.outcome = "win" if (open_trade.return_pct or 0) > 0 else "loss"
            trades.append(open_trade)

        return curve, trades

    def _signal(
        self,
        history: list[DailyScore],
        index: int,
        strategy_name: str,
        threshold: float,
        exit_threshold: float,
        momentum_window: int,
        momentum_delta: float,
        in_position: bool,
    ) -> str:
        row = history[index]
        if strategy_name == "score_momentum":
            if index < momentum_window:
                return "hold"
            delta = row.overall_score - history[index - momentum_window].overall_score
            if not in_position and delta >= momentum_delta:
                return "buy"
            if in_position and (delta <= 0 or row.overall_score < exit_threshold):
                return "sell"
            return "hold"

        if not in_position and row.overall_score > threshold:
            return "buy"
        if in_position and row.overall_score < exit_threshold:
            return "sell"
        return "hold"
