"""Matching endpoints for the matching and partnership creation flow."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_active_user
from app.schemas.matching import (
    QueueStatusResponse,
    MatchSuggestionsResponse,
    AcceptMatchRequest,
    DeclineMatchRequest,
    PartnershipCreatedResponse,
    PartnerInfo,
    MatchSuggestion
)
from app.services.match_queue_service import (
    enter_match_queue,
    get_queue_status,
    generate_match_suggestions,
    decline_match,
    leave_queue
)
from app.services.partnership_service import (
    create_partnership,
    can_create_partnership,
    get_partner_info
)
from sqlalchemy import select, func
from app.models.match_queue import MatchQueue

router = APIRouter()


@router.post("/matching/enter-queue", response_model=QueueStatusResponse, status_code=201)
async def enter_queue(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Enter the match queue to find accountability partners.

    Requirements:
    - Profile must be complete (2+ strengths, 2+ struggles)
    - Must have < 3 active partnerships
    - Queue entry expires after 7 days
    """
    try:
        queue_entry = await enter_match_queue(db, current_user.id)

        # Get updated status
        status_data = await get_queue_status(db, current_user.id)

        return QueueStatusResponse(**status_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/matching/status", response_model=QueueStatusResponse)
async def get_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's queue status and position.

    Returns:
    - Queue status (pending, matched, expired)
    - Position in queue
    - Number of match suggestions available
    """
    status_data = await get_queue_status(db, current_user.id)

    if status_data is None:
        status_data = {
            "in_queue": False,
            "status": "not_in_queue",
            "has_suggestions": False,
            "suggestions_count": 0
        }

    return QueueStatusResponse(**status_data)


@router.get("/matching/suggestions", response_model=MatchSuggestionsResponse)
async def get_suggestions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized match suggestions based on complementarity algorithm.

    Returns top 3 matches ranked by:
    - Complementarity (50%): How well strengths/struggles align
    - Compatibility (30%): Communication style and commitment
    - Availability (20%): Schedule overlap

    Declined matches are automatically filtered out.
    """
    # Check if user is in queue
    status_data = await get_queue_status(db, current_user.id)

    if not status_data or not status_data.get('in_queue'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must be in match queue to get suggestions. Call POST /matching/enter-queue first."
        )

    # Generate suggestions
    suggestions_data = await generate_match_suggestions(db, current_user.id, limit=3)

    # Get total queue count
    total_result = await db.execute(
        select(func.count()).select_from(MatchQueue)
        .where(MatchQueue.status == 'pending')
    )
    total_in_queue = total_result.scalar()

    # Convert to Pydantic models
    suggestions = [MatchSuggestion(**s) for s in suggestions_data]

    return MatchSuggestionsResponse(
        suggestions=suggestions,
        queue_position=status_data.get('queue_position'),
        total_in_queue=total_in_queue
    )


@router.post("/matching/accept", response_model=PartnershipCreatedResponse, status_code=201)
async def accept_match(
    request: AcceptMatchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Accept a match and create a partnership.

    Creates:
    - New Partnership record (Season 1, 4-week duration)
    - Both users removed from queue
    - Active partnership count incremented for both
    - Partnership health starts at 1.0

    Validation:
    - Both users must have < 3 partnerships
    - No existing partnership between users
    - Match must be in user's suggestions
    """
    # Verify both users can create partnerships
    can_create, error = await can_create_partnership(db, current_user.id)
    if not can_create:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    can_create, error = await can_create_partnership(db, request.match_id)
    if not can_create:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Match partner cannot create partnership: {error}"
        )

    # Create partnership
    try:
        partnership = await create_partnership(db, current_user.id, request.match_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Get partner info
    from sqlalchemy import select
    from app.models.user import UserProfile

    partner_user = await get_partner_info(db, partnership, current_user.id)
    partner_profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == partner_user.id)
    )
    partner_profile = partner_profile_result.scalar_one()

    partner_info = PartnerInfo(
        id=partner_user.id,
        username=partner_user.username,
        full_name=partner_user.full_name,
        profile_picture_url=partner_user.profile_picture_url,
        strengths=partner_profile.strengths or [],
        struggles=partner_profile.struggles or []
    )

    return PartnershipCreatedResponse(
        partnership_id=partnership.id,
        partner=partner_info,
        season_number=partnership.season_number,
        season_start_date=partnership.current_season_start_date,
        season_end_date=partnership.current_season_end_date,
        status=partnership.status
    )


@router.post("/matching/decline", status_code=204)
async def decline_suggestion(
    request: DeclineMatchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Decline a match suggestion.

    The declined user will not appear in future suggestions.
    Optional reason can be provided for analytics.
    """
    try:
        await decline_match(db, current_user.id, request.match_id, request.reason)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return None


@router.delete("/matching/leave-queue", status_code=204)
async def leave_match_queue(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Leave the match queue.

    Sets queue status to 'cancelled'.
    Can re-enter queue anytime by calling POST /matching/enter-queue.
    """
    await leave_queue(db, current_user.id)
    return None
