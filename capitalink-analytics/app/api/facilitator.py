"""Facilitator analytics API endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_facilitator_service
from app.core.auth import verify_api_key
from app.schemas.analytics import (
    FacilitatorEngagementsResponse,
    FacilitatorFunnelResponse,
    FacilitatorRevenueResponse,
)
from app.services.facilitator_analytics import FacilitatorAnalyticsService

router = APIRouter(prefix="/facilitator", tags=["Facilitator Analytics"])


@router.get("/engagements", response_model=FacilitatorEngagementsResponse)
async def get_facilitator_engagements(
    service: FacilitatorAnalyticsService = Depends(get_facilitator_service),
    _api_key: str = Depends(verify_api_key),
):
    """
    Get Facilitator engagement summary.

    Returns total engagements and breakdown by status.
    """
    return await service.get_engagement_status_summary()


@router.get("/revenue", response_model=FacilitatorRevenueResponse)
async def get_facilitator_revenue(
    from_date: Optional[str] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(default=None, description="End date (YYYY-MM-DD)"),
    service: FacilitatorAnalyticsService = Depends(get_facilitator_service),
    _api_key: str = Depends(verify_api_key),
):
    """
    Get Facilitator revenue summary.

    Args:
        from_date: Start date filter (optional)
        to_date: End date filter (optional)

    Returns offer fees, success fees, and total revenue.
    """
    # Parse dates if provided
    from_datetime = datetime.fromisoformat(from_date) if from_date else None
    to_datetime = datetime.fromisoformat(to_date) if to_date else None

    return await service.get_revenue_summary(
        from_date=from_datetime,
        to_date=to_datetime,
    )


@router.get("/funnel", response_model=FacilitatorFunnelResponse)
async def get_facilitator_funnel(
    service: FacilitatorAnalyticsService = Depends(get_facilitator_service),
    _api_key: str = Depends(verify_api_key),
):
    """
    Get Facilitator buyer introduction funnel.

    Returns buyer progression through stages: introduced → NDA → teaser →
    info access → offer → closing, with conversion rates.
    """
    return await service.get_buyer_intro_funnel()
