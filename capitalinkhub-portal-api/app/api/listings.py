"""
Listing endpoints for browsing and viewing business listings.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import verify_api_key
from app.services import ListingsService, InterestService
from app.schemas.listing import ListingFilters, ListingTeaser, ListingDetail
from app.schemas.common import PaginatedResponse
from app.schemas.interest import InterestCreateRequest, InterestResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/listings", tags=["Listings"])


@router.get(
    "",
    response_model=PaginatedResponse[ListingTeaser],
    dependencies=[Depends(verify_api_key)],
    summary="Get listings with filters",
    description="Browse active business listings with optional filters for industry, region, price, etc.",
)
async def get_listings(
    industry: Optional[str] = Query(None, description="Filter by industry"),
    region: Optional[str] = Query(None, description="Filter by region"),
    min_price: Optional[float] = Query(None, description="Minimum asking price"),
    max_price: Optional[float] = Query(None, description="Maximum asking price"),
    min_revenue: Optional[float] = Query(None, description="Minimum revenue"),
    max_revenue: Optional[float] = Query(None, description="Maximum revenue"),
    status: Optional[str] = Query(None, description="Deal status filter"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated list of active listings.

    Listings are anonymized to protect seller identity.
    Only teaser-level information is returned in list view.
    """
    try:
        filters = ListingFilters(
            industry=industry,
            region=region,
            min_price=min_price,
            max_price=max_price,
            min_revenue=min_revenue,
            max_revenue=max_revenue,
            status=status,
            page=page,
            page_size=page_size,
        )

        listings_service = ListingsService(db)
        result = await listings_service.get_listings(filters)

        return result
    except Exception as e:
        logger.error(f"Error getting listings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/{listing_id}",
    response_model=ListingDetail,
    dependencies=[Depends(verify_api_key)],
    summary="Get listing detail",
    description="Get detailed information about a specific listing (still anonymized).",
)
async def get_listing_detail(
    listing_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information for a single listing.

    Returns more context than the teaser but still protects seller identity.
    """
    try:
        listings_service = ListingsService(db)
        listing = await listings_service.get_listing_detail(listing_id)

        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Listing {listing_id} not found",
            )

        return listing
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting listing detail: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post(
    "/{listing_id}/interest",
    response_model=InterestResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Express interest in a listing",
    description="Record that a buyer is interested in this listing. Creates interest record and CRM activity.",
)
async def express_interest(
    listing_id: int,
    request: InterestCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Express buyer interest in a listing.

    Creates:
    1. PortalInterest record
    2. CRM Activity for tracking

    Returns the interest record. If interest already exists, returns the existing one.
    """
    try:
        interest_service = InterestService(db)
        result = await interest_service.create_interest(listing_id, request)

        return result
    except ValueError as e:
        logger.error(f"Error creating interest: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error creating interest: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
