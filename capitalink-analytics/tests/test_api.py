"""Tests for API endpoints."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "env" in data


def test_api_requires_auth():
    """Test that analytics endpoints require authentication."""
    # Try without API key
    response = client.get("/api/v1/analytics/exit-ready/pipeline")
    assert response.status_code == 401


def test_api_with_invalid_key():
    """Test that invalid API key is rejected."""
    response = client.get(
        "/api/v1/analytics/exit-ready/pipeline",
        headers={"X-API-Key": "invalid-key"},
    )
    assert response.status_code == 401
