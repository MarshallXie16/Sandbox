"""
Tests for API authentication.
"""

import pytest
from fastapi.testclient import TestClient


def test_missing_api_key(client: TestClient):
    """
    Test that endpoints reject requests without API key.
    """
    # Try to access protected endpoint without API key
    response = client.get("/api/v1/listings")

    assert response.status_code == 422  # FastAPI validation error for missing header


def test_invalid_api_key(client: TestClient):
    """
    Test that endpoints reject requests with invalid API key.
    """
    headers = {"X-API-Key": "invalid-key-12345"}
    response = client.get("/api/v1/listings", headers=headers)

    assert response.status_code == 401
    data = response.json()
    assert "Invalid or missing API key" in data.get("detail", "")


def test_valid_api_key(client: TestClient, auth_headers: dict):
    """
    Test that valid API key allows access to protected endpoints.
    """
    response = client.get("/api/v1/listings", headers=auth_headers)

    # Should return 200 (with potentially empty results)
    # or 500 if database not configured for tests
    # The important part is it doesn't return 401 (unauthorized)
    assert response.status_code != 401
