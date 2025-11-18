"""
Interest tracking endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import verify_api_key
from app.services import InterestService
from app.schemas.interest import MemberInterest
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/members", tags=["Interests"])


@router.get(
    "/{member_id}/interests",
    response_model=list[MemberInterest],
    dependencies=[Depends(verify_api_key)],
    summary="Get member's interests",
    description="Retrieve all listings a member has expressed interest in.",
)
async def get_member_interests(
    member_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all interests for a member.

    Returns list of interests with associated listing information.
    """
    try:
        interest_service = InterestService(db)
        interests = await interest_service.get_member_interests(member_id)

        return interests
    except Exception as e:
        logger.error(f"Error getting member interests: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
