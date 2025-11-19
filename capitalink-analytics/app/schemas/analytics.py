"""Analytics API response schemas."""

from datetime import date
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Health Check
class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    env: str = Field(..., description="Environment (dev/prod)")


# Exit Ready Analytics
class ExitReadyPipelineResponse(BaseModel):
    """Exit Ready pipeline summary."""

    total_cases: int = Field(..., description="Total number of cases")
    by_status: Dict[str, int] = Field(..., description="Cases grouped by status")


class StageDuration(BaseModel):
    """Duration statistics for a stage."""

    stage: str = Field(..., description="Stage name")
    average_days: Optional[float] = Field(None, description="Average duration in days")
    median_days: Optional[float] = Field(None, description="Median duration in days")
    min_days: Optional[int] = Field(None, description="Minimum duration in days")
    max_days: Optional[int] = Field(None, description="Maximum duration in days")
    sample_size: int = Field(..., description="Number of cases in sample")


class ExitReadyDurationsResponse(BaseModel):
    """Exit Ready stage durations."""

    durations: List[StageDuration] = Field(..., description="Duration stats by stage")


class ExitReadyVolumeDataPoint(BaseModel):
    """Volume data point for a time period."""

    period: str = Field(..., description="Time period (YYYY-MM or YYYY-QN)")
    created: int = Field(default=0, description="Cases created")
    delivered: int = Field(default=0, description="Cases delivered")
    closed: int = Field(default=0, description="Cases closed")


class ExitReadyVolumeResponse(BaseModel):
    """Exit Ready case volume over time."""

    period_type: str = Field(..., description="Period type: month or quarter")
    data: List[ExitReadyVolumeDataPoint] = Field(..., description="Volume data points")


# Facilitator Analytics
class FacilitatorEngagementsResponse(BaseModel):
    """Facilitator engagements summary."""

    total_engagements: int = Field(..., description="Total engagements")
    by_status: Dict[str, int] = Field(..., description="Engagements by status")


class FacilitatorRevenueResponse(BaseModel):
    """Facilitator revenue summary."""

    total_offer_fees: float = Field(..., description="Total offer fees collected")
    total_success_fee_gross: float = Field(..., description="Total gross success fees")
    total_success_fee_net: float = Field(..., description="Total net success fees")
    total_revenue: float = Field(..., description="Total revenue")
    closed_success_count: int = Field(..., description="Number of successful closings")
    period_from: Optional[date] = Field(None, description="Start date of period")
    period_to: Optional[date] = Field(None, description="End date of period")


class BuyerIntroStage(BaseModel):
    """Buyer introduction funnel stage."""

    stage: str = Field(..., description="Stage name")
    count: int = Field(..., description="Number of buyers at this stage")
    conversion_rate: Optional[float] = Field(
        None, description="Conversion rate from previous stage"
    )


class FacilitatorFunnelResponse(BaseModel):
    """Facilitator buyer introduction funnel."""

    total_introduced_buyers: int = Field(..., description="Total introduced buyers")
    funnel_stages: List[BuyerIntroStage] = Field(..., description="Funnel stages")


# CRM Analytics
class CrmOverviewResponse(BaseModel):
    """CRM overview statistics."""

    total_contacts: int = Field(..., description="Total contacts")
    total_sellers: int = Field(..., description="Total sellers")
    total_buyers: int = Field(..., description="Total buyers")
    total_companies: int = Field(..., description="Total companies")
    total_listings: int = Field(..., description="Total listings")
    active_listings: int = Field(..., description="Active listings")
    listings_by_status: Dict[str, int] = Field(
        default_factory=dict, description="Listings by status"
    )


# Buyer Activity Analytics
class TopEngagedBuyer(BaseModel):
    """Top engaged buyer details."""

    buyer_id: UUID = Field(..., description="Buyer contact ID")
    buyer_name: Optional[str] = Field(None, description="Buyer name")
    engagement_score: float = Field(..., description="Engagement score")
    listing_views: int = Field(default=0, description="Number of listing views")
    interests_expressed: int = Field(default=0, description="Number of interests")
    offers_made: int = Field(default=0, description="Number of offers made")


class TopEngagedBuyersResponse(BaseModel):
    """Top engaged buyers."""

    buyers: List[TopEngagedBuyer] = Field(..., description="List of top buyers")
    total_count: int = Field(..., description="Total number of buyers in system")


class BuyerActivityResponse(BaseModel):
    """Buyer activity statistics."""

    total_buyers: int = Field(..., description="Total buyers")
    active_buyers_last_30_days: int = Field(..., description="Active in last 30 days")
    avg_engagement_score: float = Field(..., description="Average engagement score")
    top_buyers: List[TopEngagedBuyer] = Field(..., description="Top engaged buyers")
