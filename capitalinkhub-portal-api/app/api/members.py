"""
Member profile and resolution endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import verify_api_key
from app.services import ProfileService, EngagementService
from app.schemas.member import (
    MemberResolveRequest,
    MemberResolveResponse,
    MemberProfile,
)
from app.schemas.engagement import EngagementSummary
from app.schemas.common import ErrorResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/members", tags=["Members"])


@router.post(
    "/resolve",
    response_model=MemberResolveResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Resolve or create portal member mapping",
    description="Maps an Ultimate Member user to an IndieStack CRM contact. Creates new contact if needed.",
)
async def resolve_member(
    request: MemberResolveRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Resolve or create portal member mapping.

    This endpoint is called by WordPress/Ultimate Member to establish the
    mapping between a WordPress user and an IndieStack CRM contact.

    Process:
    1. Check if mapping already exists by um_user_id
    2. If not, search for contact by email
    3. If contact doesn't exist, create new contact
    4. Create portal member mapping
    5. Return full profile
    """
    try:
        profile_service = ProfileService(db)
        result = await profile_service.resolve_member(request)
        return result
    except ValueError as e:
        logger.error(f"Error resolving member: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error resolving member: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/{member_id}/profile",
    response_model=MemberProfile,
    dependencies=[Depends(verify_api_key)],
    summary="Get member profile",
    description="Retrieve full profile for a portal member including contact and company info.",
)
async def get_member_profile(
    member_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get full member profile by member ID.
    """
    try:
        profile_service = ProfileService(db)
        profile = await profile_service.get_member_profile(member_id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Member {member_id} not found",
            )

        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting member profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/{member_id}/engagement",
    response_model=EngagementSummary,
    dependencies=[Depends(verify_api_key)],
    summary="Get member engagement summary",
    description="Retrieve engagement score and recent activity for a member.",
)
async def get_member_engagement(
    member_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get engagement summary for a member.

    Returns engagement score, recent events, and activity statistics.
    """
    try:
        # First get the member to find contact_id
        profile_service = ProfileService(db)
        profile = await profile_service.get_member_profile(member_id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Member {member_id} not found",
            )

        # Get engagement for the contact
        engagement_service = EngagementService(db)
        summary = await engagement_service.get_engagement_summary(profile.contact_id)

        if not summary:
            # Return default/empty summary if contact has no engagement data
            return EngagementSummary(
                engagement_score=0,
                total_events=0,
                recent_events=[],
                last_activity_date=None,
                email_opens=0,
                link_clicks=0,
                form_submissions=0,
            )

        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting member engagement: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
