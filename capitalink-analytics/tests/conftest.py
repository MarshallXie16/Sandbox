"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def api_key():
    """Return a test API key."""
    return "dev-key-12345"


@pytest.fixture
def headers(api_key):
    """Return headers with API key."""
    return {"X-API-Key": api_key}
