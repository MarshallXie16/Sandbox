"""Check-in service for managing partnership check-ins."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from app.models.checkin import CheckIn
from app.models.partnership import Partnership
from app.models.user import User


async def create_checkin(
    db: AsyncSession,
    partnership_id: UUID,
    current_user_id: UUID,
    what_i_did: str,
    what_i_struggled_with: Optional[str],
    what_i_need: Optional[str],
    content_type: str,
    media_url: Optional[str]
) -> CheckIn:
    """
    Create a new check-in for a partnership.

    Args:
        db: Database session
        partnership_id: Partnership ID
        current_user_id: Current user's ID
        what_i_did: What the user accomplished
        what_i_struggled_with: What the user struggled with
        what_i_need: What the user needs from their partner
        content_type: Type of content (text, voice, photo)
        media_url: Optional media URL

    Returns:
        Created CheckIn object

    Raises:
        ValueError: If partnership not found or user not a member
    """
    # Verify partnership exists and user is a member
    result = await db.execute(
        select(Partnership).where(
            and_(
                Partnership.id == partnership_id,
                or_(
                    Partnership.user1_id == current_user_id,
                    Partnership.user2_id == current_user_id
                )
            )
        )
    )
    partnership = result.scalar_one_or_none()

    if not partnership:
        raise ValueError("Partnership not found or you are not a member")

    # Create check-in
    checkin = CheckIn(
        partnership_id=partnership_id,
        author_id=current_user_id,
        what_i_did=what_i_did,
        what_i_struggled_with=what_i_struggled_with,
        what_i_need=what_i_need,
        content_type=content_type,
        media_url=media_url,
        is_read=False
    )

    db.add(checkin)

    # Update partnership last_interaction_at
    partnership.last_interaction_at = datetime.utcnow()

    # Update user's last active timestamp
    if partnership.user1_id == current_user_id:
        partnership.user1_last_active_at = datetime.utcnow()
    else:
        partnership.user2_last_active_at = datetime.utcnow()

    await db.commit()
    await db.refresh(checkin)

    return checkin


async def get_partnership_checkins(
    db: AsyncSession,
    partnership_id: UUID,
    current_user_id: UUID,
    limit: int = 20,
    offset: int = 0
) -> Tuple[List[CheckIn], int, bool]:
    """
    Get check-ins for a partnership with pagination.

    Args:
        db: Database session
        partnership_id: Partnership ID
        current_user_id: Current user's ID
        limit: Number of check-ins per page
        offset: Offset for pagination

    Returns:
        Tuple of (check-ins list, total count, has_more)

    Raises:
        ValueError: If partnership not found or user not a member
    """
    # Verify user is a member
    result = await db.execute(
        select(Partnership).where(
            and_(
                Partnership.id == partnership_id,
                or_(
                    Partnership.user1_id == current_user_id,
                    Partnership.user2_id == current_user_id
                )
            )
        )
    )
    partnership = result.scalar_one_or_none()

    if not partnership:
        raise ValueError("Partnership not found or you are not a member")

    # Get total count
    count_result = await db.execute(
        select(CheckIn).where(CheckIn.partnership_id == partnership_id)
    )
    total = len(count_result.scalars().all())

    # Get paginated check-ins (newest first)
    query = (
        select(CheckIn)
        .where(CheckIn.partnership_id == partnership_id)
        .order_by(CheckIn.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(query)
    checkins = result.scalars().all()

    has_more = (offset + len(checkins)) < total

    return checkins, total, has_more


async def get_checkin_by_id(
    db: AsyncSession,
    checkin_id: UUID,
    current_user_id: UUID
) -> Optional[CheckIn]:
    """
    Get a check-in by ID.

    Args:
        db: Database session
        checkin_id: Check-in ID
        current_user_id: Current user's ID

    Returns:
        CheckIn object or None

    Raises:
        ValueError: If user is not a member of the partnership
    """
    # Get check-in
    result = await db.execute(
        select(CheckIn).where(CheckIn.id == checkin_id)
    )
    checkin = result.scalar_one_or_none()

    if not checkin:
        return None

    # Verify user is a member of the partnership
    partnership_result = await db.execute(
        select(Partnership).where(
            and_(
                Partnership.id == checkin.partnership_id,
                or_(
                    Partnership.user1_id == current_user_id,
                    Partnership.user2_id == current_user_id
                )
            )
        )
    )
    partnership = partnership_result.scalar_one_or_none()

    if not partnership:
        raise ValueError("You are not a member of this partnership")

    return checkin


async def mark_checkin_read(
    db: AsyncSession,
    checkin_id: UUID,
    current_user_id: UUID
) -> CheckIn:
    """
    Mark a check-in as read.

    Args:
        db: Database session
        checkin_id: Check-in ID
        current_user_id: Current user's ID

    Returns:
        Updated CheckIn object

    Raises:
        ValueError: If check-in not found or user not authorized
    """
    checkin = await get_checkin_by_id(db, checkin_id, current_user_id)

    if not checkin:
        raise ValueError("Check-in not found")

    # Only the partner (not the author) should mark as read
    if checkin.author_id == current_user_id:
        raise ValueError("You cannot mark your own check-in as read")

    checkin.is_read = True

    await db.commit()
    await db.refresh(checkin)

    return checkin


async def get_checkin_with_author(
    db: AsyncSession,
    checkin: CheckIn
) -> Tuple[CheckIn, User]:
    """
    Get check-in with author information.

    Args:
        db: Database session
        checkin: CheckIn object

    Returns:
        Tuple of (CheckIn, User)
    """
    result = await db.execute(
        select(User).where(User.id == checkin.author_id)
    )
    author = result.scalar_one()

    return checkin, author
