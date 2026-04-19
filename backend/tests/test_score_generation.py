from app.services.demo_data import generate_score_history
from app.utils.math import prospect_score


def test_score_history_ignores_social_preview_components() -> None:
    scores = generate_score_history("AAPL", 30)

    assert scores
    latest = scores[-1]
    assert latest.components.x == 50.0
    assert latest.components.reddit == 50.0
    assert latest.overall_score == prospect_score(
        latest.components.news,
        latest.components.filings,
        latest.components.macro,
    )
