"""Facilitator analytics service."""

from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from app.core.logging import get_logger
from app.repositories.facilitator_read import FacilitatorReadRepository
from app.schemas.analytics import (
    BuyerIntroStage,
    FacilitatorEngagementsResponse,
    FacilitatorFunnelResponse,
    FacilitatorRevenueResponse,
)

logger = get_logger(__name__)


class FacilitatorAnalyticsService:
    """Service for Facilitator analytics calculations."""

    def __init__(self, repository: FacilitatorReadRepository):
        """Initialize service with repository."""
        self.repository = repository

    async def get_engagement_status_summary(self) -> FacilitatorEngagementsResponse:
        """
        Get engagement counts by status.

        Returns:
            Engagement summary response
        """
        data = await self.repository.get_engagement_summary()

        return FacilitatorEngagementsResponse(
            total_engagements=data["total"],
            by_status=data["by_status"],
        )

    async def get_revenue_summary(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> FacilitatorRevenueResponse:
        """
        Get revenue summary for period.

        Args:
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            Revenue summary response
        """
        data = await self.repository.get_revenue_summary(from_date, to_date)

        return FacilitatorRevenueResponse(
            total_offer_fees=data["total_offer_fees"],
            total_success_fee_gross=data["total_success_fee_gross"],
            total_success_fee_net=data["total_success_fee_net"],
            total_revenue=data["total_revenue"],
            closed_success_count=data["closed_success_count"],
            period_from=from_date.date() if from_date else None,
            period_to=to_date.date() if to_date else None,
        )

    async def get_buyer_intro_funnel(
        self, engagement_id: Optional[UUID] = None
    ) -> FacilitatorFunnelResponse:
        """
        Get buyer introduction funnel metrics.

        Args:
            engagement_id: Filter by specific engagement (optional)

        Returns:
            Funnel response with stage conversions
        """
        funnel_data = await self.repository.get_buyer_intro_funnel(engagement_id)

        # Build funnel stages with conversion rates
        stages = [
            BuyerIntroStage(
                stage="introduced",
                count=funnel_data["introduced"],
                conversion_rate=None,  # First stage, no previous
            ),
            BuyerIntroStage(
                stage="nda_signed",
                count=funnel_data["nda_signed"],
                conversion_rate=(
                    round((funnel_data["nda_signed"] / funnel_data["introduced"]) * 100, 2)
                    if funnel_data["introduced"] > 0
                    else 0.0
                ),
            ),
            BuyerIntroStage(
                stage="teaser_sent",
                count=funnel_data["teaser_sent"],
                conversion_rate=(
                    round((funnel_data["teaser_sent"] / funnel_data["nda_signed"]) * 100, 2)
                    if funnel_data["nda_signed"] > 0
                    else 0.0
                ),
            ),
            BuyerIntroStage(
                stage="info_access",
                count=funnel_data["info_access"],
                conversion_rate=(
                    round((funnel_data["info_access"] / funnel_data["teaser_sent"]) * 100, 2)
                    if funnel_data["teaser_sent"] > 0
                    else 0.0
                ),
            ),
            BuyerIntroStage(
                stage="offer",
                count=funnel_data["offer"],
                conversion_rate=(
                    round((funnel_data["offer"] / funnel_data["info_access"]) * 100, 2)
                    if funnel_data["info_access"] > 0
                    else 0.0
                ),
            ),
            BuyerIntroStage(
                stage="closing",
                count=funnel_data["closing"],
                conversion_rate=(
                    round((funnel_data["closing"] / funnel_data["offer"]) * 100, 2)
                    if funnel_data["offer"] > 0
                    else 0.0
                ),
            ),
        ]

        return FacilitatorFunnelResponse(
            total_introduced_buyers=funnel_data["introduced"],
            funnel_stages=stages,
        )

    async def get_offer_to_close_conversion(self) -> Dict[str, float]:
        """
        Get conversion rate from offers to closings.

        Returns:
            Dictionary with offer metrics
        """
        funnel_data = await self.repository.get_buyer_intro_funnel()
        offer_data = await self.repository.get_offer_counts()

        return {
            "total_offers": offer_data["total_offers"],
            "total_closings": funnel_data["closing"],
            "conversion_rate": (
                round((funnel_data["closing"] / offer_data["total_offers"]) * 100, 2)
                if offer_data["total_offers"] > 0
                else 0.0
            ),
        }
