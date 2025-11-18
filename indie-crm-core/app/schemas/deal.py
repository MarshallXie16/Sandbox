"""Pydantic schemas for Deal"""
from typing import Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field
from app.models.deal import DealStatus
from app.models.pipeline import PipelineType


class DealBase(BaseModel):
    """Base schema for Deal"""

    name: str = Field(..., max_length=255)
    pipeline_type: PipelineType
    pipeline_id: int
    stage_id: int
    amount: Optional[float] = None
    currency: str = Field(default="USD", max_length=3)
    expected_close_date: Optional[date] = None
    owner_id: Optional[int] = None
    status: DealStatus = DealStatus.OPEN
    details: Dict[str, Any] = Field(default_factory=dict)


class DealCreate(DealBase):
    """Schema for creating a Deal"""

    pass


class DealUpdate(BaseModel):
    """Schema for updating a Deal (all fields optional)"""

    name: Optional[str] = Field(None, max_length=255)
    pipeline_type: Optional[PipelineType] = None
    pipeline_id: Optional[int] = None
    stage_id: Optional[int] = None
    amount: Optional[float] = None
    currency: Optional[str] = Field(None, max_length=3)
    expected_close_date: Optional[date] = None
    owner_id: Optional[int] = None
    status: Optional[DealStatus] = None
    details: Optional[Dict[str, Any]] = None


class DealResponse(DealBase):
    """Schema for Deal responses"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
