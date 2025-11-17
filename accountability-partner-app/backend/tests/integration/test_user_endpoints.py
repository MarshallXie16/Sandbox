"""Integration tests for user endpoints."""
import pytest
from httpx import AsyncClient
from app.models.user import User


@pytest.mark.asyncio
class TestUserEndpoints:
    """Test user management endpoints."""

    async def test_get_current_user(self, client: AsyncClient, test_user: User, auth_headers: dict):
        """Test GET /api/v1/users/me endpoint."""
        response = await client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert data["full_name"] == test_user.full_name
        assert "password_hash" not in data  # Should never return password

    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test GET /api/v1/users/me without authentication."""
        response = await client.get("/api/v1/users/me")

        assert response.status_code == 403  # FastAPI HTTPBearer returns 403
        assert "detail" in response.json()

    async def test_update_current_user_full_name(self, client: AsyncClient, auth_headers: dict):
        """Test PATCH /api/v1/users/me with full_name update."""
        response = await client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"full_name": "Updated Name"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"

    async def test_update_current_user_bio(self, client: AsyncClient, auth_headers: dict):
        """Test PATCH /api/v1/users/me with bio update."""
        bio_text = "I'm a software engineer looking to improve my fitness and fashion sense."
        response = await client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"bio": bio_text}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == bio_text

    async def test_update_current_user_timezone(self, client: AsyncClient, auth_headers: dict):
        """Test PATCH /api/v1/users/me with timezone update."""
        response = await client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"timezone": "America/New_York"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["timezone"] == "America/New_York"

    async def test_update_current_user_multiple_fields(self, client: AsyncClient, auth_headers: dict):
        """Test PATCH /api/v1/users/me with multiple fields."""
        response = await client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "full_name": "New Full Name",
                "bio": "New bio text",
                "timezone": "Europe/London"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "New Full Name"
        assert data["bio"] == "New bio text"
        assert data["timezone"] == "Europe/London"

    async def test_update_current_user_unauthorized(self, client: AsyncClient):
        """Test PATCH /api/v1/users/me without authentication."""
        response = await client.patch(
            "/api/v1/users/me",
            json={"full_name": "Hacker"}
        )

        assert response.status_code == 403

    async def test_deactivate_account(self, client: AsyncClient, auth_headers: dict):
        """Test DELETE /api/v1/users/me to deactivate account."""
        response = await client.delete("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == 204

        # Verify user can no longer access protected endpoints
        # Note: In a real test, we'd need to fetch user from DB to verify is_active=False
        # For now, just verify the endpoint returns 204
