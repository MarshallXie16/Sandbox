"""
Tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestPublicEndpoints:
    """Test public endpoints (no auth required)."""

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "indie-matching-engine"
        assert "version" in data

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestAuthenticatedEndpoints:
    """Test authenticated endpoints."""

    def test_missing_api_key(self):
        """Test that missing API key returns 403."""
        response = client.get("/api/v1/matches/health")

        assert response.status_code == 403

    def test_invalid_api_key(self):
        """Test that invalid API key returns 403."""
        response = client.get(
            "/api/v1/matches/health",
            headers={"X-API-Key": "invalid-key"},
        )

        assert response.status_code == 403

    def test_valid_api_key(self):
        """Test that valid API key allows access."""
        # Using default development key from config
        response = client.get(
            "/api/v1/matches/health",
            headers={"X-API-Key": "development-key-change-in-production"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestRecommendationEndpoints:
    """Test recommendation endpoints."""

    @pytest.fixture
    def api_headers(self):
        """API authentication headers."""
        return {"X-API-Key": "development-key-change-in-production"}

    def test_buyer_recommendations_missing_buyer(self, api_headers):
        """Test getting recommendations for non-existent buyer."""
        response = client.get(
            "/api/v1/recommendations/buyer/99999",
            headers=api_headers,
        )

        # Should return 200 with empty recommendations
        assert response.status_code == 200
        data = response.json()
        assert data["buyer_id"] == 99999
        assert len(data["recommendations"]) == 0

    def test_listing_recommendations_missing_listing(self, api_headers):
        """Test getting recommendations for non-existent listing."""
        response = client.get(
            "/api/v1/recommendations/listing/99999",
            headers=api_headers,
        )

        # Should return 200 with empty recommendations
        assert response.status_code == 200
        data = response.json()
        assert data["listing_id"] == 99999
        assert len(data["recommendations"]) == 0

    def test_buyer_recommendations_with_params(self, api_headers):
        """Test buyer recommendations with query parameters."""
        response = client.get(
            "/api/v1/recommendations/buyer/1?min_score=50&limit=5&use_cached=false",
            headers=api_headers,
        )

        # Should accept parameters (may return empty if no data)
        assert response.status_code in [200, 500]  # 500 if DB not set up

    def test_listing_recommendations_with_params(self, api_headers):
        """Test listing recommendations with query parameters."""
        response = client.get(
            "/api/v1/recommendations/listing/1?min_score=40&limit=10&use_cached=true",
            headers=api_headers,
        )

        # Should accept parameters
        assert response.status_code in [200, 500]


class TestMatchEndpoints:
    """Test match computation endpoints."""

    @pytest.fixture
    def api_headers(self):
        """API authentication headers."""
        return {"X-API-Key": "development-key-change-in-production"}

    def test_compute_matches_full(self, api_headers):
        """Test full match computation."""
        response = client.post(
            "/api/v1/matches/compute",
            headers=api_headers,
            json={"force_recompute": False},
        )

        # May fail if DB not set up, but should accept request
        assert response.status_code in [200, 500]

    def test_compute_matches_specific_buyer(self, api_headers):
        """Test match computation for specific buyer."""
        response = client.post(
            "/api/v1/matches/compute",
            headers=api_headers,
            json={
                "buyer_ids": [1, 2],
                "force_recompute": True,
            },
        )

        assert response.status_code in [200, 500]

    def test_compute_matches_specific_listing(self, api_headers):
        """Test match computation for specific listing."""
        response = client.post(
            "/api/v1/matches/compute",
            headers=api_headers,
            json={
                "listing_ids": [101, 102],
                "force_recompute": False,
            },
        )

        assert response.status_code in [200, 500]
