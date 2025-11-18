"""Pydantic schemas for Activity"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.activity import ActivityType, ActivityDirection


class ActivityBase(BaseModel):
    """Base schema for Activity"""

    type: ActivityType
    subject: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    direction: Optional[ActivityDirection] = None
    happened_at: datetime = Field(default_factory=datetime.utcnow)
    owner_id: Optional[int] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class ActivityCreate(ActivityBase):
    """Schema for creating an Activity"""

    pass


class ActivityUpdate(BaseModel):
    """Schema for updating an Activity (all fields optional)"""

    type: Optional[ActivityType] = None
    subject: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    direction: Optional[ActivityDirection] = None
    happened_at: Optional[datetime] = None
    owner_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


class ActivityResponse(ActivityBase):
    """Schema for Activity responses"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
