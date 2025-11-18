"""Pydantic schemas for Pipeline and Stage"""
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.pipeline import PipelineType


# Stage Schemas
class StageBase(BaseModel):
    """Base schema for Stage"""

    pipeline_id: int
    name: str = Field(..., max_length=100)
    order_index: int
    is_closed_won: bool = False
    is_closed_lost: bool = False


class StageCreate(StageBase):
    """Schema for creating a Stage"""

    pass


class StageUpdate(BaseModel):
    """Schema for updating a Stage (all fields optional)"""

    name: Optional[str] = Field(None, max_length=100)
    order_index: Optional[int] = None
    is_closed_won: Optional[bool] = None
    is_closed_lost: Optional[bool] = None


class StageResponse(StageBase):
    """Schema for Stage responses"""

    id: int

    class Config:
        from_attributes = True


# Pipeline Schemas
class PipelineBase(BaseModel):
    """Base schema for Pipeline"""

    name: str = Field(..., max_length=100)
    type: PipelineType
    is_active: bool = True


class PipelineCreate(PipelineBase):
    """Schema for creating a Pipeline"""

    pass


class PipelineUpdate(BaseModel):
    """Schema for updating a Pipeline (all fields optional)"""

    name: Optional[str] = Field(None, max_length=100)
    type: Optional[PipelineType] = None
    is_active: Optional[bool] = None


class PipelineResponse(PipelineBase):
    """Schema for Pipeline responses"""

    id: int
    stages: List[StageResponse] = []

    class Config:
        from_attributes = True
