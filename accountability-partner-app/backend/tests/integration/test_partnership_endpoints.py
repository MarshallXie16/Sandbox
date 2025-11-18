"""Integration tests for partnership endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.models.user import User, UserProfile
from app.models.partnership import Partnership
from app.core.security import get_password_hash
from app.core.auth import create_access_token


@pytest.mark.asyncio
async def test_list_partnerships_empty(client: AsyncClient, auth_headers: dict):
    """Test listing partnerships when user has none."""
    response = await client.get("/api/v1/partnerships", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["partnerships"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_partnerships_with_data(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User
):
    """Test listing partnerships when user has partnerships."""
    # Create another user
    user2 = User(
        email="partner@example.com",
        username="partner_user",
        full_name="Partner User",
        password_hash=get_password_hash("password123")
    )
    db_session.add(user2)
    await db_session.flush()

    # Create profiles for both users
    profile2 = UserProfile(
        user_id=user2.id,
        strengths=["fashion", "relationships"],
        struggles=["career", "fitness"],
        communication_style="supportive",
        commitment_level="moderate",
        preferred_check_in_frequency="3x_week"
    )
    db_session.add(profile2)

    # Create partnership
    partnership = Partnership(
        user1_id=test_user.id,
        user2_id=user2.id,
        status='active',
        season_number=1,
        current_season_start_date=datetime.utcnow().date(),
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date(),
        check_in_frequency='3x_week',
        check_in_days=[1, 3, 5],
        balance_score=0.5,
        engagement_score=1.0,
        last_interaction_at=datetime.utcnow()
    )
    db_session.add(partnership)
    await db_session.commit()

    # Get partnerships
    token = create_access_token(data={"sub": str(test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/partnerships", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["partnerships"]) == 1
    assert data["partnerships"][0]["partner"]["username"] == "partner_user"
    assert data["partnerships"][0]["status"] == "active"


@pytest.mark.asyncio
async def test_get_partnership_details(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User
):
    """Test getting partnership details."""
    # Create another user and partnership
    user2 = User(
        email="partner@example.com",
        username="partner_user",
        full_name="Partner User",
        password_hash=get_password_hash("password123")
    )
    db_session.add(user2)
    await db_session.flush()

    profile2 = UserProfile(
        user_id=user2.id,
        strengths=["fashion"],
        struggles=["career"],
        communication_style="direct",
        commitment_level="moderate",
        preferred_check_in_frequency="daily"
    )
    db_session.add(profile2)

    partnership = Partnership(
        user1_id=test_user.id,
        user2_id=user2.id,
        status='active',
        season_number=1,
        current_season_start_date=datetime.utcnow().date(),
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date(),
        check_in_frequency='3x_week',
        check_in_days=[1, 3, 5],
        communication_methods=['text', 'voice'],
        balance_score=0.5,
        engagement_score=1.0,
        last_interaction_at=datetime.utcnow()
    )
    db_session.add(partnership)
    await db_session.commit()
    await db_session.refresh(partnership)

    # Get partnership details
    token = create_access_token(data={"sub": str(test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(f"/api/v1/partnerships/{partnership.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["partner"]["username"] == "partner_user"
    assert data["status"] == "active"
    assert data["check_in_frequency"] == "3x_week"
    assert data["check_in_days"] == [1, 3, 5]
    assert data["communication_methods"] == ['text', 'voice']


@pytest.mark.asyncio
async def test_get_partnership_unauthorized(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User
):
    """Test getting partnership details when not a member."""
    # Create two other users and a partnership between them
    user2 = User(
        email="user2@example.com",
        username="user2",
        password_hash=get_password_hash("password123")
    )
    user3 = User(
        email="user3@example.com",
        username="user3",
        password_hash=get_password_hash("password123")
    )
    db_session.add_all([user2, user3])
    await db_session.flush()

    partnership = Partnership(
        user1_id=user2.id,
        user2_id=user3.id,
        status='active',
        season_number=1,
        current_season_start_date=datetime.utcnow().date(),
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date(),
        check_in_frequency='3x_week',
        check_in_days=[1, 3, 5],
        balance_score=0.5,
        engagement_score=1.0
    )
    db_session.add(partnership)
    await db_session.commit()

    # Try to access as test_user (not a member)
    token = create_access_token(data={"sub": str(test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(f"/api/v1/partnerships/{partnership.id}", headers=headers)
    assert response.status_code == 403
    assert "not a member" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_partnership_settings(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User
):
    """Test updating partnership settings."""
    # Create partnership
    user2 = User(
        email="partner@example.com",
        username="partner_user",
        password_hash=get_password_hash("password123")
    )
    db_session.add(user2)
    await db_session.flush()

    profile2 = UserProfile(
        user_id=user2.id,
        strengths=["fashion"],
        struggles=["career"],
        communication_style="direct",
        commitment_level="moderate",
        preferred_check_in_frequency="daily"
    )
    db_session.add(profile2)

    partnership = Partnership(
        user1_id=test_user.id,
        user2_id=user2.id,
        status='active',
        season_number=1,
        current_season_start_date=datetime.utcnow().date(),
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date(),
        check_in_frequency='3x_week',
        check_in_days=[1, 3, 5],
        balance_score=0.5,
        engagement_score=1.0
    )
    db_session.add(partnership)
    await db_session.commit()
    await db_session.refresh(partnership)

    # Update settings
    token = create_access_token(data={"sub": str(test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    update_data = {
        "check_in_frequency": "daily",
        "check_in_days": [1, 2, 3, 4, 5],
        "communication_methods": ["text", "voice", "photo"]
    }

    response = await client.patch(
        f"/api/v1/partnerships/{partnership.id}/settings",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["check_in_frequency"] == "daily"
    assert data["check_in_days"] == [1, 2, 3, 4, 5]
    assert data["communication_methods"] == ["text", "voice", "photo"]


@pytest.mark.asyncio
async def test_update_partnership_settings_validation(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User
):
    """Test updating partnership settings with invalid data."""
    # Create partnership
    user2 = User(
        email="partner@example.com",
        username="partner_user",
        password_hash=get_password_hash("password123")
    )
    db_session.add(user2)
    await db_session.flush()

    partnership = Partnership(
        user1_id=test_user.id,
        user2_id=user2.id,
        status='active',
        season_number=1,
        current_season_start_date=datetime.utcnow().date(),
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date(),
        check_in_frequency='3x_week',
        check_in_days=[1, 3, 5],
        balance_score=0.5,
        engagement_score=1.0
    )
    db_session.add(partnership)
    await db_session.commit()

    token = create_access_token(data={"sub": str(test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # Invalid frequency
    response = await client.patch(
        f"/api/v1/partnerships/{partnership.id}/settings",
        json={"check_in_frequency": "invalid"},
        headers=headers
    )
    assert response.status_code == 422

    # Invalid days (out of range)
    response = await client.patch(
        f"/api/v1/partnerships/{partnership.id}/settings",
        json={"check_in_days": [0, 8]},
        headers=headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_end_partnership(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User
):
    """Test ending a partnership."""
    # Create partnership
    user2 = User(
        email="partner@example.com",
        username="partner_user",
        password_hash=get_password_hash("password123")
    )
    db_session.add(user2)
    await db_session.flush()

    # Create profiles
    profile1 = UserProfile(
        user_id=test_user.id,
        strengths=["career"],
        struggles=["fashion"],
        active_partnerships_count=1
    )
    profile2 = UserProfile(
        user_id=user2.id,
        strengths=["fashion"],
        struggles=["career"],
        active_partnerships_count=1
    )
    db_session.add_all([profile1, profile2])

    partnership = Partnership(
        user1_id=test_user.id,
        user2_id=user2.id,
        status='active',
        season_number=1,
        current_season_start_date=datetime.utcnow().date(),
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date(),
        check_in_frequency='3x_week',
        check_in_days=[1, 3, 5],
        balance_score=0.5,
        engagement_score=1.0
    )
    db_session.add(partnership)
    await db_session.commit()
    await db_session.refresh(partnership)

    # End partnership
    token = create_access_token(data={"sub": str(test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        f"/api/v1/partnerships/{partnership.id}/end",
        json={"reason": "Completed our goals!", "give_feedback": True},
        headers=headers
    )
    assert response.status_code == 204

    # Verify partnership status changed
    await db_session.refresh(partnership)
    assert partnership.status == "completed"

    # Verify active_partnerships_count decreased
    await db_session.refresh(profile1)
    await db_session.refresh(profile2)
    assert profile1.active_partnerships_count == 0
    assert profile2.active_partnerships_count == 0


@pytest.mark.asyncio
async def test_end_partnership_already_ended(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User
):
    """Test ending a partnership that's already ended."""
    # Create partnership that's already completed
    user2 = User(
        email="partner@example.com",
        username="partner_user",
        password_hash=get_password_hash("password123")
    )
    db_session.add(user2)
    await db_session.flush()

    partnership = Partnership(
        user1_id=test_user.id,
        user2_id=user2.id,
        status='completed',  # Already completed
        season_number=1,
        current_season_start_date=datetime.utcnow().date(),
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date(),
        check_in_frequency='3x_week',
        check_in_days=[1, 3, 5],
        balance_score=0.5,
        engagement_score=1.0
    )
    db_session.add(partnership)
    await db_session.commit()

    token = create_access_token(data={"sub": str(test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        f"/api/v1/partnerships/{partnership.id}/end",
        json={"reason": "Test"},
        headers=headers
    )
    assert response.status_code == 400
    assert "already ended" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_partnership_stats(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User
):
    """Test getting partnership statistics."""
    # Create partnership
    user2 = User(
        email="partner@example.com",
        username="partner_user",
        password_hash=get_password_hash("password123")
    )
    db_session.add(user2)
    await db_session.flush()

    profile2 = UserProfile(
        user_id=user2.id,
        strengths=["fashion"],
        struggles=["career"],
        communication_style="direct",
        commitment_level="moderate",
        preferred_check_in_frequency="daily"
    )
    db_session.add(profile2)

    partnership = Partnership(
        user1_id=test_user.id,
        user2_id=user2.id,
        status='active',
        season_number=1,
        current_season_start_date=datetime.utcnow().date(),
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date(),
        check_in_frequency='3x_week',
        check_in_days=[1, 3, 5],
        balance_score=0.5,
        engagement_score=1.0,
        last_interaction_at=datetime.utcnow()
    )
    db_session.add(partnership)
    await db_session.commit()
    await db_session.refresh(partnership)

    # Get stats
    token = create_access_token(data={"sub": str(test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(f"/api/v1/partnerships/{partnership.id}/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["partnership_id"] == str(partnership.id)
    assert data["season_number"] == 1
    assert data["days_active"] >= 0
    assert data["total_check_ins"] == 0  # No check-ins yet
    assert data["total_goals"] == 0  # No goals yet
    assert data["balance_score"] == 0.5
    assert data["engagement_score"] == 1.0


@pytest.mark.asyncio
async def test_filter_partnerships_by_status(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User
):
    """Test filtering partnerships by status."""
    # Create multiple partnerships with different statuses
    user2 = User(
        email="partner1@example.com",
        username="partner1",
        password_hash=get_password_hash("password123")
    )
    user3 = User(
        email="partner2@example.com",
        username="partner2",
        password_hash=get_password_hash("password123")
    )
    db_session.add_all([user2, user3])
    await db_session.flush()

    # Active partnership
    partnership1 = Partnership(
        user1_id=test_user.id,
        user2_id=user2.id,
        status='active',
        season_number=1,
        current_season_start_date=datetime.utcnow().date(),
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date(),
        check_in_frequency='3x_week',
        check_in_days=[1, 3, 5],
        balance_score=0.5,
        engagement_score=1.0
    )

    # Completed partnership
    partnership2 = Partnership(
        user1_id=test_user.id,
        user2_id=user3.id,
        status='completed',
        season_number=1,
        current_season_start_date=datetime.utcnow().date(),
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date(),
        check_in_frequency='3x_week',
        check_in_days=[1, 3, 5],
        balance_score=0.5,
        engagement_score=1.0
    )

    db_session.add_all([partnership1, partnership2])
    await db_session.commit()

    token = create_access_token(data={"sub": str(test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # Get all partnerships
    response = await client.get("/api/v1/partnerships", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] == 2

    # Get only active partnerships
    response = await client.get("/api/v1/partnerships?status=active", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["partnerships"][0]["status"] == "active"

    # Get only completed partnerships
    response = await client.get("/api/v1/partnerships?status=completed", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["partnerships"][0]["status"] == "completed"
