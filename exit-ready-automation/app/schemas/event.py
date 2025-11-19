"""
Pydantic schemas for Exit Ready events.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    """Schema for creating an event."""
    case_id: int
    event_type: str = Field(..., min_length=1, max_length=100)
    payload: Optional[Dict[str, Any]] = None
    actor: Optional[str] = Field(None, max_length=255)


class EventResponse(BaseModel):
    """Schema for event response."""
    id: int
    case_id: int
    event_type: str
    payload: Optional[Dict[str, Any]]
    actor: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class EventList(BaseModel):
    """Schema for event list."""
    items: List[EventResponse]
    total: int


class EventTypeStats(BaseModel):
    """Schema for event type statistics."""
    event_type: str
    count: int
    last_occurrence: Optional[datetime]
