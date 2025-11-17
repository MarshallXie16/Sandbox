"""Partnership service for creating and managing partnerships."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.models.user import User, UserProfile
from app.models.partnership import Partnership
from app.models.match_queue import MatchQueue


async def create_partnership(
    db: AsyncSession,
    user1_id: UUID,
    user2_id: UUID
) -> Partnership:
    """
    Create a new partnership between two users.

    Args:
        db: Database session
        user1_id: First user's ID
        user2_id: Second user's ID

    Returns:
        Created Partnership object

    Raises:
        ValueError: If partnership cannot be created (max limit, duplicate, etc.)
    """
    # Fetch both user profiles
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id.in_([user1_id, user2_id]))
    )
    profiles = result.scalars().all()

    if len(profiles) != 2:
        raise ValueError("Both users must have profiles")

    profile_dict = {p.user_id: p for p in profiles}
    user1_profile = profile_dict.get(user1_id)
    user2_profile = profile_dict.get(user2_id)

    # Check if either user has reached max partnerships (3)
    if user1_profile.active_partnerships_count >= 3:
        raise ValueError("User 1 has reached maximum partnerships (3)")
    if user2_profile.active_partnerships_count >= 3:
        raise ValueError("User 2 has reached maximum partnerships (3)")

    # Check if partnership already exists between these users
    existing = await db.execute(
        select(Partnership).where(
            and_(
                or_(
                    and_(Partnership.user1_id == user1_id, Partnership.user2_id == user2_id),
                    and_(Partnership.user1_id == user2_id, Partnership.user2_id == user1_id)
                ),
                Partnership.status.in_(['active', 'on_hold'])
            )
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("Partnership already exists between these users")

    # Calculate season dates (4 weeks)
    now = datetime.utcnow()
    season_start = now
    season_end = now + timedelta(weeks=4)

    # Create partnership
    partnership = Partnership(
        user1_id=user1_id,
        user2_id=user2_id,
        status='active',
        season_number=1,
        current_season_start_date=season_start.date(),
        current_season_end_date=season_end.date(),
        balance_score=0.5,  # Start balanced
        engagement_score=1.0,  # Start with high engagement
        mutual_goals=[],
        check_in_days=[1, 3, 5],  # Default: Mon, Wed, Fri
        check_in_frequency='3x_week',
        last_interaction_at=now
    )

    db.add(partnership)

    # Update both users' active_partnerships_count
    user1_profile.active_partnerships_count += 1
    user2_profile.active_partnerships_count += 1

    # If either user is at max (3), set is_seeking_partner to False
    if user1_profile.active_partnerships_count >= 3:
        user1_profile.is_seeking_partner = False
    if user2_profile.active_partnerships_count >= 3:
        user2_profile.is_seeking_partner = False

    # Remove both users from match queue
    await db.execute(
        select(MatchQueue).where(
            and_(
                MatchQueue.user_id.in_([user1_id, user2_id]),
                MatchQueue.status == 'pending'
            )
        )
    )
    match_queues = (await db.execute(
        select(MatchQueue).where(MatchQueue.user_id.in_([user1_id, user2_id]))
    )).scalars().all()

    for mq in match_queues:
        mq.status = 'matched'

    await db.commit()
    await db.refresh(partnership)

    return partnership


async def can_create_partnership(
    db: AsyncSession,
    user_id: UUID
) -> tuple[bool, Optional[str]]:
    """
    Check if a user can create a new partnership.

    Args:
        db: Database session
        user_id: User's ID

    Returns:
        Tuple of (can_create: bool, error_message: Optional[str])
    """
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        return False, "User profile not found"

    if profile.active_partnerships_count >= 3:
        return False, "Maximum partnerships limit reached (3)"

    return True, None


async def get_partner_info(
    db: AsyncSession,
    partnership: Partnership,
    current_user_id: UUID
) -> Optional[User]:
    """
    Get the partner's User object from a partnership.

    Args:
        db: Database session
        partnership: Partnership object
        current_user_id: Current user's ID

    Returns:
        Partner's User object or None
    """
    partner_id = partnership.user2_id if partnership.user1_id == current_user_id else partnership.user1_id

    result = await db.execute(
        select(User).where(User.id == partner_id)
    )
    return result.scalar_one_or_none()
