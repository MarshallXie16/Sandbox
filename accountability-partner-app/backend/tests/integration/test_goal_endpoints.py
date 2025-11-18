"""Integration tests for goal endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.models.user import User, UserProfile
from app.models.partnership import Partnership
from app.core.security import get_password_hash
from app.core.auth import create_access_token


@pytest.mark.asyncio
async def test_create_individual_goal(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test creating an individual goal."""
    # Create partner and partnership
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
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date()
    )
    db_session.add(partnership)
    await db_session.commit()
    await db_session.refresh(partnership)

    # Create goal
    response = await client.post(
        f"/api/v1/partnerships/{partnership.id}/goals",
        json={
            "title": "Get promoted to Senior Engineer",
            "description": "Focus on leadership skills",
            "category": "career",
            "is_mutual": False,
            "target_date": "2026-06-01",
            "subtasks": [
                {"task": "Complete leadership course", "completed": False}
            ]
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Get promoted to Senior Engineer"
    assert data["is_mutual"] is False
    assert data["owner_id"] == str(test_user.id)
    assert data["status"] == "in_progress"
    assert len(data["subtasks"]) == 1


@pytest.mark.asyncio
async def test_create_mutual_goal(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test creating a mutual goal."""
    # Create partner and partnership
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
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date()
    )
    db_session.add(partnership)
    await db_session.commit()
    await db_session.refresh(partnership)

    # Create mutual goal
    response = await client.post(
        f"/api/v1/partnerships/{partnership.id}/goals",
        json={
            "title": "Complete 10K run together",
            "is_mutual": True,
            "category": "fitness"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Complete 10K run together"
    assert data["is_mutual"] is True
    assert data["owner_id"] is None  # Mutual goals have no owner


@pytest.mark.asyncio
async def test_list_partnership_goals(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test listing all goals for a partnership."""
    # Create partner and partnership
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
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date()
    )
    db_session.add(partnership)
    await db_session.commit()
    await db_session.refresh(partnership)

    # Create multiple goals
    await client.post(
        f"/api/v1/partnerships/{partnership.id}/goals",
        json={"title": "My goal", "is_mutual": False},
        headers=auth_headers
    )

    # Create goal as partner
    token2 = create_access_token(data={"sub": str(user2.id)})
    headers2 = {"Authorization": f"Bearer {token2}"}

    await client.post(
        f"/api/v1/partnerships/{partnership.id}/goals",
        json={"title": "Partner goal", "is_mutual": False},
        headers=headers2
    )

    await client.post(
        f"/api/v1/partnerships/{partnership.id}/goals",
        json={"title": "Mutual goal", "is_mutual": True},
        headers=auth_headers
    )

    # List all goals
    response = await client.get(
        f"/api/v1/partnerships/{partnership.id}/goals",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3


@pytest.mark.asyncio
async def test_filter_goals_by_owner(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test filtering goals by owner."""
    # Create partner and partnership
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
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date()
    )
    db_session.add(partnership)
    await db_session.commit()
    await db_session.refresh(partnership)

    # Create goals
    await client.post(
        f"/api/v1/partnerships/{partnership.id}/goals",
        json={"title": "My goal", "is_mutual": False},
        headers=auth_headers
    )

    await client.post(
        f"/api/v1/partnerships/{partnership.id}/goals",
        json={"title": "Mutual goal", "is_mutual": True},
        headers=auth_headers
    )

    # Filter my goals
    response = await client.get(
        f"/api/v1/partnerships/{partnership.id}/goals?owner=me",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["goals"][0]["title"] == "My goal"

    # Filter mutual goals
    response = await client.get(
        f"/api/v1/partnerships/{partnership.id}/goals?owner=mutual",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["goals"][0]["title"] == "Mutual goal"


@pytest.mark.asyncio
async def test_update_goal(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test updating a goal."""
    # Create partner and partnership
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
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date()
    )
    db_session.add(partnership)
    await db_session.commit()
    await db_session.refresh(partnership)

    # Create goal
    create_response = await client.post(
        f"/api/v1/partnerships/{partnership.id}/goals",
        json={"title": "Original title", "is_mutual": False},
        headers=auth_headers
    )
    goal_id = create_response.json()["id"]

    # Update goal
    response = await client.patch(
        f"/api/v1/goals/{goal_id}",
        json={
            "title": "Updated title",
            "description": "New description",
            "subtasks": [
                {"task": "Task 1", "completed": False},
                {"task": "Task 2", "completed": True}
            ]
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"
    assert data["description"] == "New description"
    assert len(data["subtasks"]) == 2


@pytest.mark.asyncio
async def test_delete_goal(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test deleting a goal."""
    # Create partner and partnership
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
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date()
    )
    db_session.add(partnership)
    await db_session.commit()
    await db_session.refresh(partnership)

    # Create goal
    create_response = await client.post(
        f"/api/v1/partnerships/{partnership.id}/goals",
        json={"title": "Goal to delete", "is_mutual": False},
        headers=auth_headers
    )
    goal_id = create_response.json()["id"]

    # Delete goal
    response = await client.delete(
        f"/api/v1/goals/{goal_id}",
        headers=auth_headers
    )

    assert response.status_code == 204

    # Verify deleted
    get_response = await client.get(
        f"/api/v1/goals/{goal_id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_complete_goal(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test completing a goal."""
    # Create partner and partnership
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
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date()
    )
    db_session.add(partnership)
    await db_session.commit()
    await db_session.refresh(partnership)

    # Create goal
    create_response = await client.post(
        f"/api/v1/partnerships/{partnership.id}/goals",
        json={"title": "Goal to complete", "is_mutual": False},
        headers=auth_headers
    )
    goal_id = create_response.json()["id"]

    # Complete goal
    response = await client.post(
        f"/api/v1/goals/{goal_id}/complete",
        json={"confirm": True},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["completed_at"] is not None


@pytest.mark.asyncio
async def test_cannot_edit_partner_goal(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test that you cannot edit your partner's goal."""
    # Create partner and partnership
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
        current_season_end_date=(datetime.utcnow() + timedelta(weeks=4)).date()
    )
    db_session.add(partnership)
    await db_session.commit()
    await db_session.refresh(partnership)

    # Create goal as partner
    token2 = create_access_token(data={"sub": str(user2.id)})
    headers2 = {"Authorization": f"Bearer {token2}"}

    create_response = await client.post(
        f"/api/v1/partnerships/{partnership.id}/goals",
        json={"title": "Partner's goal", "is_mutual": False},
        headers=headers2
    )
    goal_id = create_response.json()["id"]

    # Try to update as test_user
    response = await client.patch(
        f"/api/v1/goals/{goal_id}",
        json={"title": "Hacked title"},
        headers=auth_headers
    )

    assert response.status_code == 403
    assert "only edit your own goals" in response.json()["detail"].lower()
