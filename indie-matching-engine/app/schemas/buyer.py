"""
Pydantic schemas for buyer (contact) data.
"""

from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class BuyerProfile(BaseModel):
    """
    Buyer profile extracted from CRM contact data.
    """

    # Contact identifiers
    id: int = Field(..., description="Contact ID from CRM")
    email: Optional[EmailStr] = Field(None, description="Primary email")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")

    # Buyer preferences
    industry_preferences: List[str] = Field(
        default_factory=list,
        description="Preferred industries",
    )
    region_preferences: List[str] = Field(
        default_factory=list,
        description="Preferred regions/locations",
    )

    # Budget/deal size
    min_deal_size: Optional[float] = Field(
        None,
        description="Minimum deal size (ask price)",
        ge=0,
    )
    max_deal_size: Optional[float] = Field(
        None,
        description="Maximum deal size (ask price)",
        ge=0,
    )

    # Additional preferences
    deal_types: List[str] = Field(
        default_factory=list,
        description="Preferred deal types (asset, stock, etc.)",
    )
    experience_level: Optional[str] = Field(
        None,
        description="Experience level: first_time, some_experience, experienced, serial",
    )

    # Engagement
    engagement_score: Optional[float] = Field(
        None,
        description="Engagement score (0-100)",
        ge=0,
        le=100,
    )

    # Raw details
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        from_attributes = True


class BuyerListRequest(BaseModel):
    """Request parameters for listing buyers."""

    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    category: Optional[str] = Field(None, description="Filter by category")
    min_engagement: Optional[float] = Field(None, ge=0, le=100)
