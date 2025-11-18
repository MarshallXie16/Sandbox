"""
Pydantic schemas for downloadable resources.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ResourceResponse(BaseModel):
    """Resource metadata response."""

    slug: str = Field(..., description="Resource slug/identifier")
    title: str = Field(..., description="Resource title")
    description: Optional[str] = Field(None, description="Resource description")
    category: str = Field(..., description="Resource category (buyer, seller, general)")
    resource_type: str = Field(..., description="Resource type (pdf, template, video, etc.)")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    is_gated: bool = Field(..., description="Whether resource requires login")
    download_count: int = Field(..., description="Number of downloads")
    url: Optional[str] = Field(None, description="Download URL (if available)")

    class Config:
        from_attributes = True


class ResourceListFilters(BaseModel):
    """Query parameters for filtering resources."""

    category: Optional[str] = Field(None, description="Filter by category")
    resource_type: Optional[str] = Field(None, description="Filter by type")
    is_gated: Optional[bool] = Field(None, description="Filter by gated status")
