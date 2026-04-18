from __future__ import annotations

import re

from app.models.domain import Sentiment
from app.utils.math import clamp

POSITIVE_WORDS = {
    "beat": 1.4,
    "bullish": 1.6,
    "surge": 1.3,
    "strong": 1.1,
    "upgrade": 1.3,
    "growth": 1.0,
    "demand": 0.9,
    "acceleration": 1.4,
    "constructive": 1.1,
    "margin": 0.7,
    "raise": 1.2,
}

NEGATIVE_WORDS = {
    "miss": -1.5,
    "bearish": -1.6,
    "delay": -1.0,
    "weak": -1.1,
    "downgrade": -1.3,
    "lawsuit": -1.4,
    "dilution": -1.6,
    "competition": -0.8,
    "slowdown": -1.2,
    "risk": -0.7,
    "cut": -0.9,
}


class SentimentService:
    token_pattern = re.compile(r"[a-zA-Z']+")

    def score_text(self, text: str) -> Sentiment:
        total = 0.0
        for token in self.token_pattern.findall(text.lower()):
            total += POSITIVE_WORDS.get(token, 0.0)
            total += NEGATIVE_WORDS.get(token, 0.0)
        normalized = clamp(total / 6, -1.0, 1.0)
        if normalized >= 0.15:
            label = "bullish"
        elif normalized <= -0.15:
            label = "bearish"
        else:
            label = "neutral"
        return Sentiment(label=label, score=round(normalized, 3))

    def aggregate_sentiment(self, items: list[tuple[float, float]]) -> float:
        if not items:
            return 50.0
        weighted_sum = sum(score * weight for score, weight in items)
        weight_total = sum(weight for _, weight in items) or 1
        normalized = weighted_sum / weight_total
        return round(clamp(50 + normalized * 50), 2)
