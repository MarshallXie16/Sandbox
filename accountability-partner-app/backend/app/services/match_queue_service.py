"""Match queue service for managing the matching process."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from uuid import UUID
import json

from app.models.user import User, UserProfile
from app.models.match_queue import MatchQueue
from app.services.matching_service import (
    calculate_match_score,
    generate_match_explanation,
    rank_potential_matches
)


async def enter_match_queue(
    db: AsyncSession,
    user_id: UUID
) -> MatchQueue:
    """
    Add a user to the match queue.

    Args:
        db: Database session
        user_id: User's ID

    Returns:
        MatchQueue entry

    Raises:
        ValueError: If user cannot enter queue
    """
    # Check if user has profile
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    profile = profile_result.scalar_one_or_none()

    if not profile:
        raise ValueError("User must complete profile before entering queue")

    # Check if user has max partnerships
    if profile.active_partnerships_count >= 3:
        raise ValueError("Cannot enter queue with 3 active partnerships")

    # Check if user has minimum profile data
    if not profile.strengths or len(profile.strengths) < 2:
        raise ValueError("Must have at least 2 strengths to enter queue")
    if not profile.struggles or len(profile.struggles) < 2:
        raise ValueError("Must have at least 2 struggles to enter queue")

    # Check if already in queue
    existing_result = await db.execute(
        select(MatchQueue).where(
            and_(
                MatchQueue.user_id == user_id,
                MatchQueue.status == 'pending'
            )
        )
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        # Refresh expiration
        existing.expires_at = datetime.utcnow() + timedelta(days=7)
        await db.commit()
        await db.refresh(existing)
        return existing

    # Create new queue entry
    queue_entry = MatchQueue(
        user_id=user_id,
        status='pending',
        priority_score=0.5,  # Default priority
        proposed_matches=[],
        declined_user_ids=[],
        expires_at=datetime.utcnow() + timedelta(days=7)
    )

    db.add(queue_entry)
    await db.commit()
    await db.refresh(queue_entry)

    return queue_entry


async def get_queue_status(
    db: AsyncSession,
    user_id: UUID
) -> Optional[Dict]:
    """
    Get user's queue status.

    Args:
        db: Database session
        user_id: User's ID

    Returns:
        Queue status dict or None
    """
    result = await db.execute(
        select(MatchQueue).where(MatchQueue.user_id == user_id)
        .order_by(MatchQueue.created_at.desc())
    )
    queue_entry = result.scalar_one_or_none()

    if not queue_entry:
        return {
            "in_queue": False,
            "status": "not_in_queue",
            "has_suggestions": False,
            "suggestions_count": 0
        }

    # Get total queue count for position calculation
    total_result = await db.execute(
        select(func.count()).select_from(MatchQueue)
        .where(MatchQueue.status == 'pending')
    )
    total_in_queue = total_result.scalar()

    # Calculate approximate position (by priority score and created_at)
    position_result = await db.execute(
        select(func.count()).select_from(MatchQueue)
        .where(
            and_(
                MatchQueue.status == 'pending',
                or_(
                    MatchQueue.priority_score > queue_entry.priority_score,
                    and_(
                        MatchQueue.priority_score == queue_entry.priority_score,
                        MatchQueue.created_at < queue_entry.created_at
                    )
                )
            )
        )
    )
    queue_position = position_result.scalar() + 1 if queue_entry.status == 'pending' else None

    suggestions_count = len(queue_entry.proposed_matches) if queue_entry.proposed_matches else 0

    return {
        "in_queue": queue_entry.status == 'pending',
        "status": queue_entry.status,
        "queue_position": queue_position,
        "entered_at": queue_entry.created_at,
        "expires_at": queue_entry.expires_at,
        "has_suggestions": suggestions_count > 0,
        "suggestions_count": suggestions_count
    }


async def generate_match_suggestions(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 3
) -> List[Dict]:
    """
    Generate match suggestions for a user.

    Args:
        db: Database session
        user_id: User's ID
        limit: Maximum number of suggestions

    Returns:
        List of match suggestion dicts
    """
    # Get user's profile
    user_profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    user_profile = user_profile_result.scalar_one_or_none()

    if not user_profile:
        return []

    # Get user's queue entry to check declined users
    queue_result = await db.execute(
        select(MatchQueue).where(
            and_(
                MatchQueue.user_id == user_id,
                MatchQueue.status == 'pending'
            )
        )
    )
    queue_entry = queue_result.scalar_one_or_none()

    if not queue_entry:
        return []

    declined_ids = queue_entry.declined_user_ids or []

    # Get all other users in queue (excluding declined and self)
    excluded_ids = [user_id] + [UUID(uid) if isinstance(uid, str) else uid for uid in declined_ids]

    candidates_result = await db.execute(
        select(UserProfile, User)
        .join(User, UserProfile.user_id == User.id)
        .join(MatchQueue, MatchQueue.user_id == UserProfile.user_id)
        .where(
            and_(
                MatchQueue.status == 'pending',
                ~UserProfile.user_id.in_(excluded_ids),
                UserProfile.active_partnerships_count < 3,
                UserProfile.is_seeking_partner == True
            )
        )
    )
    candidates = candidates_result.all()

    if not candidates:
        return []

    # Calculate match scores for all candidates
    candidate_profiles = [c[0] for c in candidates]
    candidate_users = {c[0].user_id: c[1] for c in candidates}

    # Rank candidates
    ranked = rank_potential_matches(user_profile, candidate_profiles, top_n=limit)

    # Build suggestions with user info
    suggestions = []
    for match in ranked:
        candidate_profile = match['user_profile']
        user = candidate_users[candidate_profile.user_id]

        suggestions.append({
            "user_id": user.id,
            "username": user.username,
            "profile_picture_url": user.profile_picture_url,
            "compatibility_score": match['match_score'],
            "strengths": candidate_profile.strengths or [],
            "struggles": candidate_profile.struggles or [],
            "communication_style": candidate_profile.communication_style,
            "commitment_level": candidate_profile.commitment_level,
            "why_matched": match['explanation']
        })

    return suggestions


async def decline_match(
    db: AsyncSession,
    user_id: UUID,
    declined_user_id: UUID,
    reason: Optional[str] = None
) -> bool:
    """
    Decline a match suggestion.

    Args:
        db: Database session
        user_id: Current user's ID
        declined_user_id: User to decline
        reason: Optional reason for declining

    Returns:
        True if successful
    """
    # Get queue entry
    result = await db.execute(
        select(MatchQueue).where(
            and_(
                MatchQueue.user_id == user_id,
                MatchQueue.status == 'pending'
            )
        )
    )
    queue_entry = result.scalar_one_or_none()

    if not queue_entry:
        raise ValueError("User not in queue")

    # Add to declined list
    declined_ids = queue_entry.declined_user_ids or []
    declined_user_id_str = str(declined_user_id)

    if declined_user_id_str not in declined_ids:
        declined_ids.append(declined_user_id_str)
        queue_entry.declined_user_ids = declined_ids

        await db.commit()

    return True


async def leave_queue(
    db: AsyncSession,
    user_id: UUID
) -> bool:
    """
    Remove user from match queue.

    Args:
        db: Database session
        user_id: User's ID

    Returns:
        True if successful
    """
    result = await db.execute(
        select(MatchQueue).where(
            and_(
                MatchQueue.user_id == user_id,
                MatchQueue.status == 'pending'
            )
        )
    )
    queue_entry = result.scalar_one_or_none()

    if queue_entry:
        queue_entry.status = 'cancelled'
        await db.commit()

    return True
