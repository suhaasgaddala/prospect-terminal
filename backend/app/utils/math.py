def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def pct_change(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100


def scale_unit_to_score(value: float) -> float:
    centered = 50 + (value * 50)
    return round(clamp(centered), 2)


def max_drawdown(values: list[float]) -> float:
    peak = values[0] if values else 1.0
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        if peak:
            drawdown = (value - peak) / peak
            worst = min(worst, drawdown)
    return round(abs(worst) * 100, 2)
