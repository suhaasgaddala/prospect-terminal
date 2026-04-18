from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Prospect Terminal API"


def test_stock_endpoint_demo_mode() -> None:
    response = client.get("/api/stock?ticker=NVDA")
    assert response.status_code == 200
    payload = response.json()
    assert payload["quote"]["ticker"] == "NVDA"
    assert payload["thesis"]["rating"] in {"bullish", "neutral", "bearish"}
