"""
Tests for health check endpoint.
"""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """
    Test that health check endpoint returns OK.
    """
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "env" in data


def test_health_check_no_auth_required(client: TestClient):
    """
    Test that health check does not require authentication.
    """
    # Should work without API key
    response = client.get("/api/v1/health")
    assert response.status_code == 200
