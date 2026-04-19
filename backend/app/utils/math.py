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


def prospect_score(news: float, filings: float, macro: float) -> float:
    # Preserve the relative importance of the real inputs after removing preview-only social lanes.
    return round((news * 25 + filings * 20 + macro * 20) / 65, 2)
