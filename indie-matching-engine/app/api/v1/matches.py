"""
Match computation and batch processing endpoints.
"""

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.api.deps import get_matching_engine, verify_api_key
from app.core.matching_engine import MatchingEngine
from app.schemas.match import BatchMatchRequest, BatchMatchResponse

router = APIRouter()


@router.post(
    "/compute",
    response_model=BatchMatchResponse,
    summary="Compute and cache match scores",
    description="Triggers batch computation of match scores and caches them for fast retrieval.",
)
async def compute_matches(
    request: BatchMatchRequest,
    background_tasks: BackgroundTasks,
    engine: MatchingEngine = Depends(get_matching_engine),
    _api_key: str = Depends(verify_api_key),
) -> BatchMatchResponse:
    """
    Compute match scores in batch and cache them.

    This endpoint triggers computation of match scores for buyer-listing pairs.
    Results are cached in the database for fast retrieval by recommendation endpoints.

    Use this endpoint to:
    - Pre-compute matches for all active buyers and listings
    - Refresh matches for specific buyers or listings
    - Force recomputation of stale matches
    """
    try:
        matching_run = await engine.compute_and_cache_matches(
            buyer_ids=request.buyer_ids,
            listing_ids=request.listing_ids,
            force_recompute=request.force_recompute,
        )

        return BatchMatchResponse(
            matching_run_id=matching_run.id,
            status=matching_run.status,
            matches_computed=matching_run.matches_computed or 0,
            buyers_processed=matching_run.buyers_processed or 0,
            listings_processed=matching_run.listings_processed or 0,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute matches: {str(e)}")


@router.get(
    "/health",
    summary="Health check",
    description="Simple health check endpoint to verify the service is running.",
)
async def health_check(_api_key: str = Depends(verify_api_key)) -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "indie-matching-engine"}
