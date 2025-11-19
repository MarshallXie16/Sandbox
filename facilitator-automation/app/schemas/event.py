"""
Pydantic schemas for Events (audit trail).
"""

from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import Field

from app.schemas.base import BaseSchema
from app.models.enums import EventType


class EventBase(BaseSchema):
    """Base event schema with common fields."""

    event_type: EventType = Field(..., description="Type of event")
    payload: Optional[Dict[str, Any]] = Field(None, description="Structured event data")
    description: Optional[str] = Field(None, description="Human-readable description")
    actor: Optional[str] = Field(None, description="User or system that triggered the event")


class EventCreate(EventBase):
    """Schema for creating a new event."""

    engagement_id: Optional[int] = None
    buyer_intro_id: Optional[int] = None
    offer_id: Optional[int] = None
    closing_id: Optional[int] = None


class EventResponse(EventBase):
    """Schema for event response."""

    id: int
    engagement_id: Optional[int] = None
    buyer_intro_id: Optional[int] = None
    offer_id: Optional[int] = None
    closing_id: Optional[int] = None
    created_at: datetime = Field(..., description="Event timestamp")


class EventFilter(BaseSchema):
    """Schema for filtering events."""

    engagement_id: Optional[int] = None
    buyer_intro_id: Optional[int] = None
    offer_id: Optional[int] = None
    closing_id: Optional[int] = None
    event_type: Optional[EventType] = None
    actor: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
