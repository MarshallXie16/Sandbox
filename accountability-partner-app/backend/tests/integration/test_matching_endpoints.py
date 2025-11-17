"""Integration tests for matching endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserProfile
from app.core.security import get_password_hash
from app.core.auth import create_access_token


class TestMatchingFlow:
    """Test the complete matching flow from queue entry to partnership creation."""

    @pytest.mark.asyncio
    async def test_enter_queue_success(self, client: AsyncClient, test_user: User, auth_headers: dict, db_session: AsyncSession):
        """Test successfully entering the match queue."""
        # First complete the profile with required fields
        profile_data = {
            "strengths": ["career", "fitness"],
            "struggles": ["fashion", "relationships"],
            "communication_style": "direct",
            "commitment_level": "moderate"
        }
        await client.patch("/api/v1/profiles/me", json=profile_data, headers=auth_headers)

        # Enter queue
        response = await client.post("/api/v1/matching/enter-queue", headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["in_queue"] is True
        assert data["status"] == "pending"
        assert data["has_suggestions"] is False

    @pytest.mark.asyncio
    async def test_enter_queue_without_complete_profile(self, client: AsyncClient, test_user: User, auth_headers: dict):
        """Test entering queue without completing profile fails."""
        response = await client.post("/api/v1/matching/enter-queue", headers=auth_headers)

        assert response.status_code == 400
        assert "strengths" in response.json()["detail"] or "struggles" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_queue_status(self, client: AsyncClient, test_user: User, auth_headers: dict):
        """Test getting queue status."""
        # Complete profile
        profile_data = {
            "strengths": ["career", "fitness"],
            "struggles": ["fashion", "relationships"]
        }
        await client.patch("/api/v1/profiles/me", json=profile_data, headers=auth_headers)

        # Enter queue
        await client.post("/api/v1/matching/enter-queue", headers=auth_headers)

        # Get status
        response = await client.get("/api/v1/matching/status", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["in_queue"] is True
        assert data["status"] == "pending"
        assert "queue_position" in data

    @pytest.mark.asyncio
    async def test_get_suggestions_not_in_queue(self, client: AsyncClient, test_user: User, auth_headers: dict):
        """Test getting suggestions when not in queue fails."""
        response = await client.get("/api/v1/matching/suggestions", headers=auth_headers)

        assert response.status_code == 400
        assert "Must be in match queue" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_complete_matching_flow(self, client: AsyncClient, db_session: AsyncSession):
        """Test complete flow: two users enter queue, get suggestions, accept match."""
        # Create two users with complementary profiles
        user1 = User(
            email="user1@test.com",
            username="user1",
            password_hash=get_password_hash("pass123")
        )
        user2 = User(
            email="user2@test.com",
            username="user2",
            password_hash=get_password_hash("pass123")
        )
        db_session.add_all([user1, user2])
        await db_session.flush()

        # Create profiles
        profile1 = UserProfile(
            user_id=user1.id,
            strengths=["career", "fitness"],
            struggles=["fashion", "relationships"],
            communication_style="direct",
            commitment_level="moderate"
        )
        profile2 = UserProfile(
            user_id=user2.id,
            strengths=["fashion", "relationships"],  # Complementary!
            struggles=["career", "fitness"],  # Complementary!
            communication_style="supportive",
            commitment_level="moderate"
        )
        db_session.add_all([profile1, profile2])
        await db_session.commit()

        # Create auth tokens
        token1 = create_access_token(data={"sub": str(user1.id)})
        token2 = create_access_token(data={"sub": str(user2.id)})
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}

        # Both users enter queue
        response1 = await client.post("/api/v1/matching/enter-queue", headers=headers1)
        response2 = await client.post("/api/v1/matching/enter-queue", headers=headers2)

        assert response1.status_code == 201
        assert response2.status_code == 201

        # User1 gets suggestions
        response = await client.get("/api/v1/matching/suggestions", headers=headers1)

        assert response.status_code == 200
        data = response.json()
        assert len(data["suggestions"]) >= 1
        assert data["total_in_queue"] == 2

        # Check that user2 is in suggestions
        suggestion = data["suggestions"][0]
        assert suggestion["user_id"] == str(user2.id)
        assert suggestion["username"] == "user2"
        assert suggestion["compatibility_score"] > 0.5  # Should be high match
        assert "why_matched" in suggestion

        # User1 accepts the match
        accept_response = await client.post(
            "/api/v1/matching/accept",
            json={"match_id": str(user2.id)},
            headers=headers1
        )

        assert accept_response.status_code == 201
        partnership_data = accept_response.json()
        assert "partnership_id" in partnership_data
        assert partnership_data["partner"]["username"] == "user2"
        assert partnership_data["season_number"] == 1
        assert partnership_data["status"] == "active"

        # Verify both users are out of queue
        status1 = await client.get("/api/v1/matching/status", headers=headers1)
        status2 = await client.get("/api/v1/matching/status", headers=headers2)

        assert status1.json()["status"] == "matched"
        assert status2.json()["status"] == "matched"

    @pytest.mark.asyncio
    async def test_decline_match(self, client: AsyncClient, db_session: AsyncSession):
        """Test declining a match suggestion."""
        # Create two users
        user1 = User(
            email="decline1@test.com",
            username="decline1",
            password_hash=get_password_hash("pass123")
        )
        user2 = User(
            email="decline2@test.com",
            username="decline2",
            password_hash=get_password_hash("pass123")
        )
        db_session.add_all([user1, user2])
        await db_session.flush()

        # Create profiles
        profile1 = UserProfile(
            user_id=user1.id,
            strengths=["career", "fitness"],
            struggles=["fashion", "relationships"]
        )
        profile2 = UserProfile(
            user_id=user2.id,
            strengths=["fashion", "relationships"],
            struggles=["career", "fitness"]
        )
        db_session.add_all([profile1, profile2])
        await db_session.commit()

        # Create auth
        token1 = create_access_token(data={"sub": str(user1.id)})
        headers1 = {"Authorization": f"Bearer {token1}"}

        # Both enter queue
        await client.post("/api/v1/matching/enter-queue", headers=headers1)
        token2 = create_access_token(data={"sub": str(user2.id)})
        headers2 = {"Authorization": f"Bearer {token2}"}
        await client.post("/api/v1/matching/enter-queue", headers=headers2)

        # User1 gets suggestions
        suggestions = await client.get("/api/v1/matching/suggestions", headers=headers1)
        assert len(suggestions.json()["suggestions"]) >= 1

        # User1 declines user2
        decline_response = await client.post(
            "/api/v1/matching/decline",
            json={"match_id": str(user2.id), "reason": "Not a good fit"},
            headers=headers1
        )

        assert decline_response.status_code == 204

        # Verify user2 is no longer in suggestions
        new_suggestions = await client.get("/api/v1/matching/suggestions", headers=headers1)
        suggestion_ids = [s["user_id"] for s in new_suggestions.json()["suggestions"]]
        assert str(user2.id) not in suggestion_ids

    @pytest.mark.asyncio
    async def test_max_partnerships_limit(self, client: AsyncClient, db_session: AsyncSession):
        """Test that users with 3 partnerships cannot enter queue."""
        # Create user with 3 partnerships
        user = User(
            email="maxed@test.com",
            username="maxed",
            password_hash=get_password_hash("pass123")
        )
        db_session.add(user)
        await db_session.flush()

        profile = UserProfile(
            user_id=user.id,
            strengths=["career", "fitness"],
            struggles=["fashion", "relationships"],
            active_partnerships_count=3  # At max
        )
        db_session.add(profile)
        await db_session.commit()

        # Try to enter queue
        token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post("/api/v1/matching/enter-queue", headers=headers)

        assert response.status_code == 400
        assert "3 active partnerships" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_leave_queue(self, client: AsyncClient, test_user: User, auth_headers: dict):
        """Test leaving the match queue."""
        # Complete profile and enter queue
        profile_data = {
            "strengths": ["career", "fitness"],
            "struggles": ["fashion", "relationships"]
        }
        await client.patch("/api/v1/profiles/me", json=profile_data, headers=auth_headers)
        await client.post("/api/v1/matching/enter-queue", headers=auth_headers)

        # Leave queue
        response = await client.delete("/api/v1/matching/leave-queue", headers=auth_headers)

        assert response.status_code == 204

        # Verify status updated
        status = await client.get("/api/v1/matching/status", headers=auth_headers)
        assert status.json()["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_duplicate_partnership_prevention(self, client: AsyncClient, db_session: AsyncSession):
        """Test that duplicate partnerships cannot be created."""
        # Create two users
        user1 = User(
            email="dup1@test.com",
            username="dup1",
            password_hash=get_password_hash("pass123")
        )
        user2 = User(
            email="dup2@test.com",
            username="dup2",
            password_hash=get_password_hash("pass123")
        )
        db_session.add_all([user1, user2])
        await db_session.flush()

        # Create profiles
        profile1 = UserProfile(
            user_id=user1.id,
            strengths=["career", "fitness"],
            struggles=["fashion", "relationships"]
        )
        profile2 = UserProfile(
            user_id=user2.id,
            strengths=["fashion", "relationships"],
            struggles=["career", "fitness"]
        )
        db_session.add_all([profile1, profile2])
        await db_session.commit()

        # Create first partnership manually
        from app.models.partnership import Partnership
        from datetime import datetime, timedelta
        partnership = Partnership(
            user1_id=user1.id,
            user2_id=user2.id,
            status='active',
            season_number=1,
            current_season_start_date=datetime.utcnow().date(),
            current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date()
        )
        db_session.add(partnership)
        profile1.active_partnerships_count = 1
        profile2.active_partnerships_count = 1
        await db_session.commit()

        # Try to create duplicate
        token1 = create_access_token(data={"sub": str(user1.id)})
        headers1 = {"Authorization": f"Bearer {token1}"}

        # Both enter queue
        await client.post("/api/v1/matching/enter-queue", headers=headers1)
        token2 = create_access_token(data={"sub": str(user2.id)})
        headers2 = {"Authorization": f"Bearer {token2}"}
        await client.post("/api/v1/matching/enter-queue", headers=headers2)

        # Try to accept (should fail)
        response = await client.post(
            "/api/v1/matching/accept",
            json={"match_id": str(user2.id)},
            headers=headers1
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
