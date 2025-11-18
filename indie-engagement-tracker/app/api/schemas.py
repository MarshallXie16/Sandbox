"""Pydantic schemas for API request/response models."""
from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field


# Scoring Profile Schemas
class ScoringProfileCreate(BaseModel):
    """Schema for creating a scoring profile."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    rules: Dict[str, Any] = Field(..., description="Scoring rules as JSON")
    is_default: bool = False


class ScoringProfileUpdate(BaseModel):
    """Schema for updating a scoring profile."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None


class ScoringProfileResponse(BaseModel):
    """Schema for scoring profile response."""

    id: int
    name: str
    description: Optional[str]
    rules: Dict[str, Any]
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Engagement Schemas
class EngagementEntityResponse(BaseModel):
    """Schema for engagement entity response."""

    id: int
    external_id: str
    entity_type: str
    latest_score: float
    score_breakdown: Optional[Dict[str, Any]]
    last_activity_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EngagementEventResponse(BaseModel):
    """Schema for engagement event response."""

    id: int
    external_id: str
    entity_type: str
    source_system: str
    event_type: str
    weight: float
    metadata: Optional[Dict[str, Any]]
    occurred_at: datetime
    ingested_at: datetime

    class Config:
        from_attributes = True


# Ingest Schemas
class IngestRequest(BaseModel):
    """Schema for ingestion request."""

    since: Optional[datetime] = Field(
        None, description="Only ingest events after this datetime"
    )
    limit: Optional[int] = Field(None, ge=1, description="Max events per source")
    dry_run: bool = Field(False, description="Don't save to database")


class IngestResponse(BaseModel):
    """Schema for ingestion response."""

    total_fetched: int
    total_new: int
    total_duplicates: int
    total_errors: int
    dry_run: bool
    sources: Dict[str, Dict[str, int]]


# Score Calculation Schemas
class RecalculateRequest(BaseModel):
    """Schema for score recalculation request."""

    profile_id: Optional[int] = Field(None, description="Scoring profile to use")
    entity_type: Optional[str] = Field(None, description="Filter by entity type")
    min_events: int = Field(0, ge=0, description="Min events required")


class RecalculateResponse(BaseModel):
    """Schema for recalculation response."""

    total_entities: int
    recalculated: int
    skipped: int
    errors: int


# Top Contacts Schemas
class TopContactsRequest(BaseModel):
    """Schema for top contacts request."""

    limit: int = Field(50, ge=1, le=1000)
    min_score: Optional[float] = None
    since: Optional[datetime] = None
    entity_type: Optional[str] = None


class TopContactsResponse(BaseModel):
    """Schema for top contacts response."""

    entities: List[EngagementEntityResponse]
    total: int


# Entity Detail Schemas
class EntityDetailResponse(BaseModel):
    """Schema for entity detail response."""

    entity: EngagementEntityResponse
    recent_events: List[EngagementEventResponse]
    score_history: List[Dict[str, Any]]


# Statistics Schema
class StatisticsResponse(BaseModel):
    """Schema for statistics response."""

    total_entities: int
    total_events: int
    average_score: float
    by_entity_type: Dict[str, int]
    active_last_30_days: int
