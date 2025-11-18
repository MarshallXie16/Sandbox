"""
Recommendation endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_matching_engine, verify_api_key
from app.core.matching_engine import MatchingEngine
from app.schemas.recommendation import RecommendationResponse

router = APIRouter()


@router.get(
    "/buyer/{buyer_id}",
    response_model=RecommendationResponse,
    summary="Get listing recommendations for a buyer",
    description="Returns ranked listing recommendations for a specific buyer based on match scores.",
)
async def get_buyer_recommendations(
    buyer_id: int,
    min_score: Optional[float] = Query(
        None,
        ge=0,
        le=100,
        description="Minimum match score threshold",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Maximum number of recommendations",
    ),
    use_cached: bool = Query(
        True,
        description="Use cached match scores if available",
    ),
    engine: MatchingEngine = Depends(get_matching_engine),
    _api_key: str = Depends(verify_api_key),
) -> RecommendationResponse:
    """
    Get listing recommendations for a buyer.

    This endpoint returns the best matching listings for a given buyer,
    ranked by match score. It considers factors like industry preferences,
    region, deal size, experience level, and engagement.
    """
    try:
        return await engine.get_recommendations_for_buyer(
            buyer_id=buyer_id,
            min_score=min_score,
            limit=limit,
            use_cached=use_cached,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.get(
    "/listing/{listing_id}",
    response_model=RecommendationResponse,
    summary="Get buyer recommendations for a listing",
    description="Returns ranked buyer recommendations for a specific listing based on match scores.",
)
async def get_listing_recommendations(
    listing_id: int,
    min_score: Optional[float] = Query(
        None,
        ge=0,
        le=100,
        description="Minimum match score threshold",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Maximum number of recommendations",
    ),
    use_cached: bool = Query(
        True,
        description="Use cached match scores if available",
    ),
    engine: MatchingEngine = Depends(get_matching_engine),
    _api_key: str = Depends(verify_api_key),
) -> RecommendationResponse:
    """
    Get buyer recommendations for a listing.

    This endpoint returns the best matching buyers for a given listing,
    ranked by match score. Useful for identifying qualified buyers for
    a specific deal.
    """
    try:
        return await engine.get_recommendations_for_listing(
            listing_id=listing_id,
            min_score=min_score,
            limit=limit,
            use_cached=use_cached,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")
