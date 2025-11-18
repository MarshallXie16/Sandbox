"""Integration tests for check-in endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.models.user import User
from app.models.partnership import Partnership
from app.core.security import get_password_hash
from app.core.auth import create_access_token


@pytest.mark.asyncio
async def test_create_checkin(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test creating a check-in."""
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

    # Create check-in
    response = await client.post(
        f"/api/v1/partnerships/{partnership.id}/check-ins",
        json={
            "what_i_did": "Applied to 5 senior roles this week",
            "what_i_struggled_with": "Imposter syndrome during interviews",
            "what_i_need": "Help with leadership questions",
            "content_type": "text"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["what_i_did"] == "Applied to 5 senior roles this week"
    assert data["what_i_struggled_with"] == "Imposter syndrome during interviews"
    assert data["what_i_need"] == "Help with leadership questions"
    assert data["content_type"] == "text"
    assert data["is_read"] is False
    assert data["author"]["username"] == test_user.username

    # Verify partnership timestamp was updated
    await db_session.refresh(partnership)
    assert partnership.last_interaction_at is not None
    assert partnership.user1_last_active_at is not None


@pytest.mark.asyncio
async def test_create_checkin_with_media(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test creating a check-in with media content."""
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

    # Create check-in with voice content
    response = await client.post(
        f"/api/v1/partnerships/{partnership.id}/check-ins",
        json={
            "what_i_did": "Recorded progress update",
            "content_type": "voice",
            "media_url": "https://storage.example.com/audio/checkin123.mp3"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content_type"] == "voice"
    assert data["media_url"] == "https://storage.example.com/audio/checkin123.mp3"


@pytest.mark.asyncio
async def test_list_checkins(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test listing check-ins with pagination."""
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

    # Create multiple check-ins
    for i in range(5):
        await client.post(
            f"/api/v1/partnerships/{partnership.id}/check-ins",
            json={
                "what_i_did": f"Update {i+1}",
                "content_type": "text"
            },
            headers=auth_headers
        )

    # List check-ins
    response = await client.get(
        f"/api/v1/partnerships/{partnership.id}/check-ins",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["check_ins"]) == 5
    assert data["has_more"] is False
    # Verify all check-ins are present
    what_i_dids = [checkin["what_i_did"] for checkin in data["check_ins"]]
    for i in range(1, 6):
        assert f"Update {i}" in what_i_dids


@pytest.mark.asyncio
async def test_list_checkins_pagination(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test check-in pagination."""
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

    # Create 25 check-ins
    for i in range(25):
        await client.post(
            f"/api/v1/partnerships/{partnership.id}/check-ins",
            json={
                "what_i_did": f"Update {i+1}",
                "content_type": "text"
            },
            headers=auth_headers
        )

    # First page
    response = await client.get(
        f"/api/v1/partnerships/{partnership.id}/check-ins?limit=10&offset=0",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 25
    assert len(data["check_ins"]) == 10
    assert data["has_more"] is True

    # Second page
    response = await client.get(
        f"/api/v1/partnerships/{partnership.id}/check-ins?limit=10&offset=10",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["check_ins"]) == 10
    assert data["has_more"] is True


@pytest.mark.asyncio
async def test_get_checkin(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test getting a specific check-in."""
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

    # Create check-in
    create_response = await client.post(
        f"/api/v1/partnerships/{partnership.id}/check-ins",
        json={
            "what_i_did": "Completed project milestone",
            "what_i_struggled_with": "Time management",
            "what_i_need": "Better planning tools",
            "content_type": "text"
        },
        headers=auth_headers
    )
    checkin_id = create_response.json()["id"]

    # Get check-in
    response = await client.get(
        f"/api/v1/check-ins/{checkin_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == checkin_id
    assert data["what_i_did"] == "Completed project milestone"
    assert data["author"]["username"] == test_user.username


@pytest.mark.asyncio
async def test_mark_checkin_read(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test marking a check-in as read."""
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

    # Create check-in as test_user
    create_response = await client.post(
        f"/api/v1/partnerships/{partnership.id}/check-ins",
        json={
            "what_i_did": "Finished sprint tasks",
            "content_type": "text"
        },
        headers=auth_headers
    )
    checkin_id = create_response.json()["id"]

    # Partner marks it as read
    token2 = create_access_token(data={"sub": str(user2.id)})
    headers2 = {"Authorization": f"Bearer {token2}"}

    response = await client.patch(
        f"/api/v1/check-ins/{checkin_id}/read",
        headers=headers2
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is True


@pytest.mark.asyncio
async def test_author_cannot_mark_own_checkin_read(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test that author cannot mark their own check-in as read."""
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

    # Create check-in
    create_response = await client.post(
        f"/api/v1/partnerships/{partnership.id}/check-ins",
        json={
            "what_i_did": "Completed tasks",
            "content_type": "text"
        },
        headers=auth_headers
    )
    checkin_id = create_response.json()["id"]

    # Try to mark own check-in as read
    response = await client.patch(
        f"/api/v1/check-ins/{checkin_id}/read",
        headers=auth_headers
    )

    assert response.status_code == 403
    assert "cannot mark your own check-in" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_non_member_cannot_access_checkins(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test that non-partnership members cannot access check-ins."""
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

    # Create outsider user
    user3 = User(
        email="outsider@example.com",
        username="outsider_user",
        password_hash=get_password_hash("password123")
    )
    db_session.add(user3)
    await db_session.commit()

    token3 = create_access_token(data={"sub": str(user3.id)})
    headers3 = {"Authorization": f"Bearer {token3}"}

    # Try to create check-in
    response = await client.post(
        f"/api/v1/partnerships/{partnership.id}/check-ins",
        json={
            "what_i_did": "Hacking attempt",
            "content_type": "text"
        },
        headers=headers3
    )

    assert response.status_code == 400
    assert "not found or you are not a member" in response.json()["detail"].lower()

    # Try to list check-ins
    response = await client.get(
        f"/api/v1/partnerships/{partnership.id}/check-ins",
        headers=headers3
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_invalid_content_type(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict
):
    """Test that invalid content types are rejected."""
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

    # Try invalid content type
    response = await client.post(
        f"/api/v1/partnerships/{partnership.id}/check-ins",
        json={
            "what_i_did": "Test",
            "content_type": "invalid_type"
        },
        headers=auth_headers
    )

    assert response.status_code == 422  # Validation error
