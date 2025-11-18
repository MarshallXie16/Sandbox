"""Partnership service for creating and managing partnerships."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from uuid import UUID

from app.models.user import User, UserProfile
from app.models.partnership import Partnership
from app.models.match_queue import MatchQueue
from app.models.checkin import CheckIn
from app.models.goal import Goal


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


async def is_partnership_member(
    db: AsyncSession,
    partnership_id: UUID,
    user_id: UUID
) -> bool:
    """
    Check if a user is a member of a partnership.

    Args:
        db: Database session
        partnership_id: Partnership ID
        user_id: User's ID

    Returns:
        True if user is a member, False otherwise
    """
    result = await db.execute(
        select(Partnership).where(
            and_(
                Partnership.id == partnership_id,
                or_(
                    Partnership.user1_id == user_id,
                    Partnership.user2_id == user_id
                )
            )
        )
    )
    return result.scalar_one_or_none() is not None


async def get_user_partnerships(
    db: AsyncSession,
    user_id: UUID,
    status_filter: Optional[str] = None
) -> List[Partnership]:
    """
    Get all partnerships for a user.

    Args:
        db: Database session
        user_id: User's ID
        status_filter: Optional status filter ('active', 'completed', etc.)

    Returns:
        List of Partnership objects
    """
    query = select(Partnership).where(
        or_(
            Partnership.user1_id == user_id,
            Partnership.user2_id == user_id
        )
    )

    if status_filter:
        query = query.where(Partnership.status == status_filter)

    query = query.order_by(Partnership.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


async def get_partnership_by_id(
    db: AsyncSession,
    partnership_id: UUID
) -> Optional[Partnership]:
    """
    Get a partnership by ID.

    Args:
        db: Database session
        partnership_id: Partnership ID

    Returns:
        Partnership object or None
    """
    result = await db.execute(
        select(Partnership).where(Partnership.id == partnership_id)
    )
    return result.scalar_one_or_none()


async def update_partnership_settings(
    db: AsyncSession,
    partnership_id: UUID,
    check_in_frequency: Optional[str] = None,
    check_in_days: Optional[List[int]] = None,
    communication_methods: Optional[List[str]] = None
) -> Partnership:
    """
    Update partnership settings.

    Args:
        db: Database session
        partnership_id: Partnership ID
        check_in_frequency: Optional check-in frequency
        check_in_days: Optional check-in days
        communication_methods: Optional communication methods

    Returns:
        Updated Partnership object

    Raises:
        ValueError: If partnership not found
    """
    partnership = await get_partnership_by_id(db, partnership_id)

    if not partnership:
        raise ValueError("Partnership not found")

    if check_in_frequency is not None:
        partnership.check_in_frequency = check_in_frequency

    if check_in_days is not None:
        partnership.check_in_days = check_in_days

    if communication_methods is not None:
        partnership.communication_methods = communication_methods

    await db.commit()
    await db.refresh(partnership)

    return partnership


async def end_partnership(
    db: AsyncSession,
    partnership_id: UUID,
    reason: Optional[str] = None
) -> Partnership:
    """
    End a partnership gracefully.

    Args:
        db: Database session
        partnership_id: Partnership ID
        reason: Optional reason for ending

    Returns:
        Updated Partnership object

    Raises:
        ValueError: If partnership not found or already ended
    """
    partnership = await get_partnership_by_id(db, partnership_id)

    if not partnership:
        raise ValueError("Partnership not found")

    if partnership.status in ['completed', 'cancelled']:
        raise ValueError("Partnership already ended")

    # Update partnership status
    partnership.status = 'completed'

    # Decrement active_partnerships_count for both users
    result = await db.execute(
        select(UserProfile).where(
            UserProfile.user_id.in_([partnership.user1_id, partnership.user2_id])
        )
    )
    profiles = result.scalars().all()

    for profile in profiles:
        if profile.active_partnerships_count > 0:
            profile.active_partnerships_count -= 1
        # If below max, allow seeking partner again
        if profile.active_partnerships_count < 3:
            profile.is_seeking_partner = True

    await db.commit()
    await db.refresh(partnership)

    return partnership


async def get_partnership_stats(
    db: AsyncSession,
    partnership_id: UUID,
    current_user_id: UUID
) -> Dict:
    """
    Get partnership analytics.

    Args:
        db: Database session
        partnership_id: Partnership ID
        current_user_id: Current user's ID

    Returns:
        Dictionary with partnership stats

    Raises:
        ValueError: If partnership not found
    """
    partnership = await get_partnership_by_id(db, partnership_id)

    if not partnership:
        raise ValueError("Partnership not found")

    # Get partner ID
    partner_id = partnership.user2_id if partnership.user1_id == current_user_id else partnership.user1_id

    # Calculate days active
    days_active = (datetime.utcnow() - partnership.created_at).days

    # Get check-in counts
    checkin_result = await db.execute(
        select(func.count(CheckIn.id)).where(CheckIn.partnership_id == partnership_id)
    )
    total_check_ins = checkin_result.scalar() or 0

    user_checkin_result = await db.execute(
        select(func.count(CheckIn.id)).where(
            and_(
                CheckIn.partnership_id == partnership_id,
                CheckIn.author_id == current_user_id
            )
        )
    )
    user_check_ins = user_checkin_result.scalar() or 0

    partner_checkin_result = await db.execute(
        select(func.count(CheckIn.id)).where(
            and_(
                CheckIn.partnership_id == partnership_id,
                CheckIn.author_id == partner_id
            )
        )
    )
    partner_check_ins = partner_checkin_result.scalar() or 0

    # Get goal counts
    goal_result = await db.execute(
        select(func.count(Goal.id)).where(Goal.partnership_id == partnership_id)
    )
    total_goals = goal_result.scalar() or 0

    completed_goal_result = await db.execute(
        select(func.count(Goal.id)).where(
            and_(
                Goal.partnership_id == partnership_id,
                Goal.status == 'completed'
            )
        )
    )
    completed_goals = completed_goal_result.scalar() or 0

    # Calculate streaks (simplified - would need more complex logic for real streaks)
    current_streak = 0
    longest_streak = 0

    return {
        "partnership_id": partnership_id,
        "season_number": partnership.season_number,
        "days_active": days_active,
        "total_check_ins": total_check_ins,
        "user_check_ins": user_check_ins,
        "partner_check_ins": partner_check_ins,
        "total_goals": total_goals,
        "completed_goals": completed_goals,
        "balance_score": partnership.balance_score,
        "engagement_score": partnership.engagement_score,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "last_interaction_at": partnership.last_interaction_at
    }
