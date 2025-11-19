"""
VaultAI Integration Layer - CRM Schemas
Pydantic models for CRM and matching AI services.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MatchingRequest(BaseModel):
    """Request to find matching partners."""

    entity_type: str = Field(
        ...,
        description="Type of entity (buyer, seller, company)",
    )
    entity_data: Dict[str, Any] = Field(
        ...,
        description="Entity characteristics for matching",
    )
    candidate_pool: List[Dict[str, Any]] = Field(
        ...,
        description="Pool of candidates to match against",
        min_length=1,
    )
    criteria: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Matching criteria and weights",
    )


class MatchResult(BaseModel):
    """Single match result."""

    entity_id: str = Field(
        ...,
        description="Matched entity ID",
    )
    score: float = Field(
        ...,
        description="Match score (0-1)",
        ge=0.0,
        le=1.0,
    )
    reasoning: str = Field(
        ...,
        description="Explanation of match",
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Match strengths",
    )
    concerns: List[str] = Field(
        default_factory=list,
        description="Potential concerns",
    )


class MatchingResponse(BaseModel):
    """Response with matching results."""

    matches: List[MatchResult] = Field(
        ...,
        description="Ranked list of matches",
    )
    total_evaluated: int = Field(
        ...,
        description="Total candidates evaluated",
    )


class EnrichProfileRequest(BaseModel):
    """Request to enrich entity profile."""

    entity_id: str = Field(
        ...,
        description="Entity identifier",
    )
    entity_data: Dict[str, Any] = Field(
        ...,
        description="Current entity data",
    )
    enrichment_type: str = Field(
        ...,
        description="Type of enrichment (summary, insights, recommendations)",
    )


class EnrichProfileResponse(BaseModel):
    """Response with enriched profile."""

    enriched_data: Dict[str, Any] = Field(
        ...,
        description="Enriched entity data",
    )
    insights: List[str] = Field(
        default_factory=list,
        description="Generated insights",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations",
    )
