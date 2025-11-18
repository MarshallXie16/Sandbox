"""
Pydantic schemas for match scores.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MatchScoreComponents(BaseModel):
    """
    Breakdown of match score components.
    """

    industry_score: float = Field(default=0.0, description="Industry match score")
    region_score: float = Field(default=0.0, description="Region match score")
    deal_size_score: float = Field(default=0.0, description="Deal size alignment score")
    experience_score: float = Field(default=0.0, description="Experience match score")
    engagement_score: float = Field(default=0.0, description="Engagement boost score")

    class Config:
        from_attributes = True


class MatchScore(BaseModel):
    """
    Match score between a buyer and a listing.
    """

    buyer_id: int = Field(..., description="Buyer (contact) ID")
    listing_id: int = Field(..., description="Listing (deal) ID")

    score: float = Field(..., description="Overall match score (0-100)", ge=0, le=100)

    components: MatchScoreComponents = Field(
        ...,
        description="Score component breakdown",
    )

    reason_codes: List[str] = Field(
        default_factory=list,
        description="Human-readable reasons for the match",
    )

    # Optional cached data
    buyer_email: Optional[str] = Field(None, description="Buyer email (cached)")
    listing_name: Optional[str] = Field(None, description="Listing name (cached)")

    # Metadata
    computed_at: Optional[datetime] = Field(None, description="When score was computed")

    class Config:
        from_attributes = True


class BatchMatchRequest(BaseModel):
    """Request for batch match computation."""

    buyer_ids: Optional[List[int]] = Field(
        None,
        description="Specific buyer IDs (if None, process all active buyers)",
    )
    listing_ids: Optional[List[int]] = Field(
        None,
        description="Specific listing IDs (if None, process all active listings)",
    )
    force_recompute: bool = Field(
        default=False,
        description="Force recomputation even if cached scores exist",
    )


class BatchMatchResponse(BaseModel):
    """Response from batch match computation."""

    matching_run_id: int = Field(..., description="ID of the matching run")
    status: str = Field(..., description="Run status")
    matches_computed: int = Field(..., description="Number of matches computed")
    buyers_processed: int = Field(..., description="Buyers processed")
    listings_processed: int = Field(..., description="Listings processed")
