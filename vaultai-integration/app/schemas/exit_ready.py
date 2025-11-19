"""
VaultAI Integration Layer - Exit Ready Schemas
Pydantic models for Exit Ready module AI services.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TeaserRequest(BaseModel):
    """Request to generate investment teaser."""

    company_name: str = Field(
        ...,
        description="Company name",
        min_length=1,
    )
    industry: str = Field(
        ...,
        description="Industry sector",
    )
    revenue: Optional[float] = Field(
        default=None,
        description="Annual revenue in millions",
    )
    ebitda: Optional[float] = Field(
        default=None,
        description="EBITDA in millions",
    )
    year_founded: Optional[int] = Field(
        default=None,
        description="Year company was founded",
    )
    employees: Optional[int] = Field(
        default=None,
        description="Number of employees",
    )
    description: str = Field(
        ...,
        description="Brief company description",
        min_length=10,
    )
    unique_selling_points: Optional[List[str]] = Field(
        default=None,
        description="List of USPs",
    )
    additional_context: Optional[str] = Field(
        default=None,
        description="Any additional context to include",
    )


class TeaserResponse(BaseModel):
    """Response with generated teaser."""

    teaser: str = Field(
        ...,
        description="Generated investment teaser",
    )
    word_count: int = Field(
        ...,
        description="Word count of teaser",
    )
    pii_detected: Dict[str, int] = Field(
        default_factory=dict,
        description="Detected PII types and counts",
    )


class ChecklistRequest(BaseModel):
    """Request to generate exit readiness checklist."""

    company_name: str = Field(
        ...,
        description="Company name",
    )
    industry: str = Field(
        ...,
        description="Industry sector",
    )
    revenue: Optional[float] = Field(
        default=None,
        description="Annual revenue in millions",
    )
    exit_timeline_months: Optional[int] = Field(
        default=None,
        description="Planned exit timeline in months",
    )
    current_challenges: Optional[List[str]] = Field(
        default=None,
        description="Known challenges or gaps",
    )


class ChecklistItem(BaseModel):
    """Single checklist item."""

    category: str = Field(
        ...,
        description="Category (Financial, Legal, Operational, etc.)",
    )
    item: str = Field(
        ...,
        description="Checklist item description",
    )
    priority: str = Field(
        ...,
        description="Priority level (High, Medium, Low)",
    )
    estimated_time: Optional[str] = Field(
        default=None,
        description="Estimated time to complete",
    )


class ChecklistResponse(BaseModel):
    """Response with exit readiness checklist."""

    checklist: List[ChecklistItem] = Field(
        ...,
        description="List of checklist items",
    )
    summary: str = Field(
        ...,
        description="Overall assessment summary",
    )


class SummaryRequest(BaseModel):
    """Request to summarize exit readiness data."""

    company_name: str = Field(
        ...,
        description="Company name",
    )
    data: Dict[str, Any] = Field(
        ...,
        description="Exit readiness data to summarize",
    )
    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="Specific areas to focus on in summary",
    )


class SummaryResponse(BaseModel):
    """Response with summary."""

    summary: str = Field(
        ...,
        description="Generated summary",
    )
    key_findings: List[str] = Field(
        default_factory=list,
        description="Key findings extracted from data",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommended next steps",
    )
