"""Tests for GET /health and API error handling."""

from fastapi.testclient import TestClient

from src.api.app import create_app


def test_health_returns_ok() -> None:
    """GET /health returns 200 with status='ok' and corpus_version."""
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "corpus_version" in data
    assert isinstance(data["corpus_version"], int)


def test_ask_stub_returns_consistent_error_shape() -> None:
    """POST /ask stub returns 501 with the standard {detail, code} error payload."""
    app = create_app()
    with TestClient(app) as client:
        response = client.post("/ask", json={"query": "What is the refund policy?"})

    assert response.status_code == 501
    data = response.json()
    assert "detail" in data
    assert data["code"] == "HTTP_501"

