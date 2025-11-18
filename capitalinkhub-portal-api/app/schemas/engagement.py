"""
Pydantic schemas for engagement tracking and activity.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class EngagementEvent(BaseModel):
    """Single engagement event."""

    event_type: str = Field(..., description="Event type (email_open, click, form_submit, etc.)")
    occurred_at: datetime = Field(..., description="When event occurred")
    subject: Optional[str] = Field(None, description="Event subject/title")
    description: Optional[str] = Field(None, description="Event description")
    metadata: Optional[dict] = Field(None, description="Additional event metadata")

    class Config:
        from_attributes = True


class EngagementSummary(BaseModel):
    """
    Engagement summary for a member.

    Includes score and recent activity.
    """

    engagement_score: int = Field(..., description="Overall engagement score (0-100)")
    total_events: int = Field(..., description="Total number of engagement events")
    recent_events: list[EngagementEvent] = Field(
        ..., description="Recent engagement events (last 10)"
    )
    last_activity_date: Optional[datetime] = Field(
        None, description="Date of most recent activity"
    )
    email_opens: int = Field(0, description="Total email opens")
    link_clicks: int = Field(0, description="Total link clicks")
    form_submissions: int = Field(0, description="Total form submissions")
