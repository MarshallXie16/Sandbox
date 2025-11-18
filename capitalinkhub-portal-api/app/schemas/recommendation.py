"""
Pydantic schemas for listing recommendations.
"""

from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.listing import ListingTeaser


class RecommendationScore(BaseModel):
    """Recommendation with match score."""

    listing: ListingTeaser = Field(..., description="Recommended listing")
    match_score: float = Field(
        ..., ge=0, le=100, description="Match score (0-100)"
    )
    match_reasons: list[str] = Field(
        ..., description="Reasons for recommendation"
    )


class RecommendationsResponse(BaseModel):
    """Response containing member recommendations."""

    member_id: int = Field(..., description="Portal member ID")
    recommendations: list[RecommendationScore] = Field(
        ..., description="List of recommended listings"
    )
    total_recommendations: int = Field(..., description="Total number of recommendations")
    algorithm: str = Field(
        default="heuristic", description="Recommendation algorithm used"
    )
