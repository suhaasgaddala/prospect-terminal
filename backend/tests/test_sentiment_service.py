from app.services.sentiment_service import SentimentService


def test_sentiment_service_detects_bullish_text() -> None:
    service = SentimentService()
    result = service.score_text("Analysts upgrade the stock after strong demand and a beat.")
    assert result.label == "bullish"
    assert result.score > 0


def test_sentiment_service_detects_bearish_text() -> None:
    service = SentimentService()
    result = service.score_text("The company faces dilution risk after a weak quarter miss.")
    assert result.label == "bearish"
    assert result.score < 0
