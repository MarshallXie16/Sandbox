"""
Recommendation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import verify_api_key
from app.services import RecommendationService
from app.schemas.recommendation import RecommendationsResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/members", tags=["Recommendations"])


@router.get(
    "/{member_id}/recommendations",
    response_model=RecommendationsResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Get personalized recommendations",
    description="Get personalized listing recommendations for a member based on their interests and preferences.",
)
async def get_recommendations(
    member_id: int,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recommendations"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get personalized recommendations for a member.

    Uses a heuristic algorithm based on past interests.
    Future: Will integrate with indie-matching-engine for ML-based recommendations.
    """
    try:
        recommendation_service = RecommendationService(db)
        result = await recommendation_service.get_recommendations(member_id, limit=limit)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Member {member_id} not found",
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
