"""Pydantic schemas for Project model."""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class ProjectBase(BaseModel):
    """Base schema for Project."""
    project_name: str
    business_name: str
    industry: str
    currency: str = "CAD"
    description: Optional[str] = None
    advisor_notes: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a new Project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a Project."""
    project_name: Optional[str] = None
    business_name: Optional[str] = None
    industry: Optional[str] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    advisor_notes: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Schema for Project response."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
