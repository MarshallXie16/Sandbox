"""Integration tests for profile endpoints."""
import pytest
from httpx import AsyncClient
from app.models.user import User


@pytest.mark.asyncio
class TestProfileEndpoints:
    """Test profile management endpoints."""

    async def test_get_current_user_profile(self, client: AsyncClient, test_user: User, auth_headers: dict):
        """Test GET /api/v1/profiles/me endpoint."""
        response = await client.get("/api/v1/profiles/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(test_user.id)
        assert "strengths" in data
        assert "struggles" in data
        assert data["active_partnerships_count"] == 0
        assert data["max_partnerships"] == 3
        assert data["is_seeking_partner"] is True

    async def test_get_profile_unauthorized(self, client: AsyncClient):
        """Test GET /api/v1/profiles/me without authentication."""
        response = await client.get("/api/v1/profiles/me")

        assert response.status_code == 403

    async def test_update_profile_strengths_and_struggles(self, client: AsyncClient, auth_headers: dict):
        """Test PATCH /api/v1/profiles/me with strengths and struggles."""
        response = await client.patch(
            "/api/v1/profiles/me",
            headers=auth_headers,
            json={
                "strengths": ["career", "fitness"],
                "struggles": ["fashion", "relationships"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert set(data["strengths"]) == {"career", "fitness"}
        assert set(data["struggles"]) == {"fashion", "relationships"}

    async def test_update_profile_validation_min_strengths(self, client: AsyncClient, auth_headers: dict):
        """Test PATCH /api/v1/profiles/me with insufficient strengths."""
        response = await client.patch(
            "/api/v1/profiles/me",
            headers=auth_headers,
            json={
                "strengths": ["career"]  # Only 1, need 2-4
            }
        )

        assert response.status_code == 422  # Validation error
        assert "detail" in response.json()

    async def test_update_profile_validation_max_strengths(self, client: AsyncClient, auth_headers: dict):
        """Test PATCH /api/v1/profiles/me with too many strengths."""
        response = await client.patch(
            "/api/v1/profiles/me",
            headers=auth_headers,
            json={
                "strengths": ["career", "fitness", "finance", "fashion", "cooking"]  # 5 items, max is 4
            }
        )

        assert response.status_code == 422  # Validation error

    async def test_update_profile_communication_style(self, client: AsyncClient, auth_headers: dict):
        """Test PATCH /api/v1/profiles/me with communication style."""
        response = await client.patch(
            "/api/v1/profiles/me",
            headers=auth_headers,
            json={
                "communication_style": "direct"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["communication_style"] == "direct"

    async def test_update_profile_invalid_communication_style(self, client: AsyncClient, auth_headers: dict):
        """Test PATCH /api/v1/profiles/me with invalid communication style."""
        response = await client.patch(
            "/api/v1/profiles/me",
            headers=auth_headers,
            json={
                "communication_style": "invalid_style"
            }
        )

        assert response.status_code == 422
        assert "communication_style must be one of" in str(response.json())

    async def test_update_profile_commitment_level(self, client: AsyncClient, auth_headers: dict):
        """Test PATCH /api/v1/profiles/me with commitment level."""
        for level in ["casual", "moderate", "intense"]:
            response = await client.patch(
                "/api/v1/profiles/me",
                headers=auth_headers,
                json={
                    "commitment_level": level
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["commitment_level"] == level

    async def test_update_profile_invalid_commitment_level(self, client: AsyncClient, auth_headers: dict):
        """Test PATCH /api/v1/profiles/me with invalid commitment level."""
        response = await client.patch(
            "/api/v1/profiles/me",
            headers=auth_headers,
            json={
                "commitment_level": "super_intense"
            }
        )

        assert response.status_code == 422

    async def test_update_profile_check_in_frequency(self, client: AsyncClient, auth_headers: dict):
        """Test PATCH /api/v1/profiles/me with check-in frequency."""
        for frequency in ["daily", "3x_week", "weekly"]:
            response = await client.patch(
                "/api/v1/profiles/me",
                headers=auth_headers,
                json={
                    "preferred_check_in_frequency": frequency
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["preferred_check_in_frequency"] == frequency

    async def test_update_profile_available_days(self, client: AsyncClient, auth_headers: dict):
        """Test PATCH /api/v1/profiles/me with available days."""
        response = await client.patch(
            "/api/v1/profiles/me",
            headers=auth_headers,
            json={
                "available_days_of_week": [1, 3, 5]  # Mon, Wed, Fri
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["available_days_of_week"] == [1, 3, 5]

    async def test_update_profile_invalid_days(self, client: AsyncClient, auth_headers: dict):
        """Test PATCH /api/v1/profiles/me with invalid day numbers."""
        response = await client.patch(
            "/api/v1/profiles/me",
            headers=auth_headers,
            json={
                "available_days_of_week": [0, 8]  # Invalid: must be 1-7
            }
        )

        assert response.status_code == 422
        assert "Days must be between 1" in str(response.json())

    async def test_update_profile_check_in_time(self, client: AsyncClient, auth_headers: dict):
        """Test PATCH /api/v1/profiles/me with preferred check-in time."""
        for time in ["morning", "afternoon", "evening"]:
            response = await client.patch(
                "/api/v1/profiles/me",
                headers=auth_headers,
                json={
                    "preferred_check_in_time": time
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["preferred_check_in_time"] == time

    async def test_update_profile_complete_onboarding(self, client: AsyncClient, auth_headers: dict):
        """Test complete profile update (simulating onboarding)."""
        response = await client.patch(
            "/api/v1/profiles/me",
            headers=auth_headers,
            json={
                "strengths": ["career", "fitness"],
                "struggles": ["fashion", "relationships"],
                "communication_style": "direct",
                "commitment_level": "moderate",
                "preferred_check_in_frequency": "3x_week",
                "available_days_of_week": [1, 3, 5],
                "preferred_check_in_time": "evening"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["strengths"] == ["career", "fitness"]
        assert data["struggles"] == ["fashion", "relationships"]
        assert data["communication_style"] == "direct"
        assert data["commitment_level"] == "moderate"
        assert data["preferred_check_in_frequency"] == "3x_week"
        assert data["available_days_of_week"] == [1, 3, 5]
        assert data["preferred_check_in_time"] == "evening"
        assert data["is_seeking_partner"] is True  # Should be set to true when updating

    async def test_update_profile_sets_seeking_partner(self, client: AsyncClient, auth_headers: dict):
        """Test that updating profile sets is_seeking_partner to True."""
        response = await client.patch(
            "/api/v1/profiles/me",
            headers=auth_headers,
            json={
                "strengths": ["career", "fitness"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_seeking_partner"] is True
