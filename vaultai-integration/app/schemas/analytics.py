"""
VaultAI Integration Layer - Analytics Schemas
Pydantic models for Analytics module AI services.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class GenerateInsightsRequest(BaseModel):
    """Request to generate insights from analytics data."""

    data_type: str = Field(
        ...,
        description="Type of data (deals, users, revenue, engagement)",
    )
    data: Dict[str, Any] = Field(
        ...,
        description="Analytics data to analyze",
    )
    time_period: Optional[str] = Field(
        default=None,
        description="Time period covered (e.g., '2024-Q1', 'last_30_days')",
    )
    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="Specific areas to focus on",
    )


class GenerateInsightsResponse(BaseModel):
    """Response with generated insights."""

    insights: List[str] = Field(
        ...,
        description="Key insights extracted from data",
    )
    trends: List[str] = Field(
        default_factory=list,
        description="Identified trends",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable recommendations",
    )
    summary: str = Field(
        ...,
        description="Overall summary",
    )


class GenerateReportRequest(BaseModel):
    """Request to generate analytics report."""

    report_type: str = Field(
        ...,
        description="Type of report (weekly, monthly, quarterly, custom)",
    )
    data: Dict[str, Any] = Field(
        ...,
        description="Data for report",
    )
    sections: Optional[List[str]] = Field(
        default=None,
        description="Sections to include",
    )
    format: Optional[str] = Field(
        default="markdown",
        description="Output format (markdown, html, text)",
    )


class GenerateReportResponse(BaseModel):
    """Response with generated report."""

    report: str = Field(
        ...,
        description="Generated report content",
    )
    format: str = Field(
        ...,
        description="Report format",
    )
    word_count: int = Field(
        ...,
        description="Word count",
    )


class ExplainMetricRequest(BaseModel):
    """Request to explain a metric or trend."""

    metric_name: str = Field(
        ...,
        description="Name of metric to explain",
    )
    current_value: Any = Field(
        ...,
        description="Current metric value",
    )
    historical_values: Optional[List[Any]] = Field(
        default=None,
        description="Historical values for context",
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context",
    )


class ExplainMetricResponse(BaseModel):
    """Response with metric explanation."""

    explanation: str = Field(
        ...,
        description="Plain-language explanation",
    )
    interpretation: str = Field(
        ...,
        description="What the metric means",
    )
    factors: List[str] = Field(
        default_factory=list,
        description="Contributing factors",
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggestions for improvement",
    )
