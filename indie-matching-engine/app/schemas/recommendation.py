"""
Pydantic schemas for recommendation requests and responses.
"""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.buyer import BuyerProfile
from app.schemas.listing import ListingProfile
from app.schemas.match import MatchScore


class RecommendationRequest(BaseModel):
    """
    Request for recommendations.
    """

    # For buyer recommendations
    buyer_id: Optional[int] = Field(
        None,
        description="Get listing recommendations for this buyer",
    )

    # For listing recommendations
    listing_id: Optional[int] = Field(
        None,
        description="Get buyer recommendations for this listing",
    )

    # Filters and options
    min_score: Optional[float] = Field(
        None,
        description="Minimum match score threshold (overrides config default)",
        ge=0,
        le=100,
    )

    limit: int = Field(
        default=10,
        description="Maximum number of recommendations",
        ge=1,
        le=100,
    )

    include_profiles: bool = Field(
        default=False,
        description="Include full buyer/listing profiles in response",
    )

    use_cached: bool = Field(
        default=True,
        description="Use cached match scores if available",
    )


class BuyerRecommendation(BaseModel):
    """
    A single listing recommendation for a buyer.
    """

    listing: ListingProfile = Field(..., description="Listing profile")
    match_score: MatchScore = Field(..., description="Match score details")


class ListingRecommendation(BaseModel):
    """
    A single buyer recommendation for a listing.
    """

    buyer: BuyerProfile = Field(..., description="Buyer profile")
    match_score: MatchScore = Field(..., description="Match score details")


class RecommendationResponse(BaseModel):
    """
    Response containing recommendations.
    """

    # Context
    buyer_id: Optional[int] = Field(None, description="Buyer ID (if applicable)")
    listing_id: Optional[int] = Field(None, description="Listing ID (if applicable)")

    # Recommendations
    recommendations: List[BuyerRecommendation | ListingRecommendation] = Field(
        default_factory=list,
        description="List of recommendations",
    )

    # Metadata
    total_candidates: int = Field(
        ...,
        description="Total number of candidates evaluated",
    )
    recommendations_count: int = Field(
        ...,
        description="Number of recommendations returned",
    )
    min_score_used: float = Field(
        ...,
        description="Minimum score threshold used",
    )
    cached: bool = Field(
        default=False,
        description="Whether cached scores were used",
    )
