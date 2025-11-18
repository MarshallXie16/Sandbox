"""Partnership endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.user import User, UserProfile
from app.core.dependencies import get_current_active_user
from app.schemas.partnership import (
    PartnershipResponse,
    PartnershipListResponse,
    PartnershipUpdateSettings,
    EndPartnershipRequest,
    PartnershipStats,
    PartnerInfo
)
from app.services.partnership_service import (
    get_user_partnerships,
    get_partnership_by_id,
    is_partnership_member,
    update_partnership_settings,
    end_partnership,
    get_partnership_stats,
    get_partner_info
)
from sqlalchemy import select

router = APIRouter()


async def get_partner_profile(db: AsyncSession, user_id: UUID) -> UserProfile:
    """Helper to get partner's profile."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def build_partnership_response(
    db: AsyncSession,
    partnership,
    current_user_id: UUID
) -> PartnershipResponse:
    """Helper to build partnership response with partner info."""
    # Get partner's user and profile
    partner_user = await get_partner_info(db, partnership, current_user_id)
    partner_profile = await get_partner_profile(db, partner_user.id)

    partner_info = PartnerInfo(
        id=partner_user.id,
        username=partner_user.username,
        full_name=partner_user.full_name,
        profile_picture_url=partner_user.profile_picture_url,
        strengths=partner_profile.strengths if partner_profile else None,
        struggles=partner_profile.struggles if partner_profile else None
    )

    return PartnershipResponse(
        id=partnership.id,
        partner=partner_info,
        status=partnership.status,
        season_number=partnership.season_number,
        current_season_start_date=partnership.current_season_start_date,
        current_season_end_date=partnership.current_season_end_date,
        mutual_goals=partnership.mutual_goals or [],
        check_in_frequency=partnership.check_in_frequency,
        check_in_days=partnership.check_in_days or [],
        communication_methods=partnership.communication_methods or [],
        balance_score=partnership.balance_score,
        engagement_score=partnership.engagement_score,
        last_interaction_at=partnership.last_interaction_at,
        created_at=partnership.created_at
    )


@router.get("/partnerships", response_model=PartnershipListResponse)
async def list_partnerships(
    status: str = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all user's partnerships.

    Query Parameters:
    - status: Filter by status (active, completed, cancelled)
    """
    partnerships = await get_user_partnerships(db, current_user.id, status_filter=status)

    partnership_responses = []
    for partnership in partnerships:
        response = await build_partnership_response(db, partnership, current_user.id)
        partnership_responses.append(response)

    return PartnershipListResponse(
        partnerships=partnership_responses,
        total=len(partnership_responses)
    )


@router.get("/partnerships/{partnership_id}", response_model=PartnershipResponse)
async def get_partnership(
    partnership_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get partnership details by ID.

    Authorization: Only partnership members can access.
    """
    # Check if user is a member
    is_member = await is_partnership_member(db, partnership_id, current_user.id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this partnership"
        )

    partnership = await get_partnership_by_id(db, partnership_id)
    if not partnership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partnership not found"
        )

    return await build_partnership_response(db, partnership, current_user.id)


@router.patch("/partnerships/{partnership_id}/settings", response_model=PartnershipResponse)
async def update_partnership(
    partnership_id: UUID,
    settings: PartnershipUpdateSettings,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update partnership settings (check-in frequency, days, communication methods).

    Authorization: Only partnership members can update.
    """
    # Check if user is a member
    is_member = await is_partnership_member(db, partnership_id, current_user.id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this partnership"
        )

    try:
        partnership = await update_partnership_settings(
            db,
            partnership_id,
            check_in_frequency=settings.check_in_frequency,
            check_in_days=settings.check_in_days,
            communication_methods=settings.communication_methods
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return await build_partnership_response(db, partnership, current_user.id)


@router.post("/partnerships/{partnership_id}/end", status_code=status.HTTP_204_NO_CONTENT)
async def end_partnership_endpoint(
    partnership_id: UUID,
    request: EndPartnershipRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    End a partnership gracefully.

    Authorization: Only partnership members can end.
    """
    # Check if user is a member
    is_member = await is_partnership_member(db, partnership_id, current_user.id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this partnership"
        )

    try:
        await end_partnership(db, partnership_id, reason=request.reason)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/partnerships/{partnership_id}/stats", response_model=PartnershipStats)
async def get_partnership_statistics(
    partnership_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get partnership analytics and statistics.

    Authorization: Only partnership members can access.
    """
    # Check if user is a member
    is_member = await is_partnership_member(db, partnership_id, current_user.id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this partnership"
        )

    try:
        stats = await get_partnership_stats(db, partnership_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    return PartnershipStats(**stats)
