"""
Pydantic schemas for buyer interest tracking.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.listing import ListingTeaser


class InterestCreateRequest(BaseModel):
    """Request to express interest in a listing."""

    member_id: int = Field(..., description="Portal member ID")
    note: Optional[str] = Field(None, description="Optional note from buyer")


class InterestResponse(BaseModel):
    """Response after creating an interest."""

    interest_id: int = Field(..., description="Interest record ID")
    member_id: int = Field(..., description="Portal member ID")
    listing_id: int = Field(..., description="Listing ID")
    status: str = Field(..., description="Interest status")
    created_at: datetime = Field(..., description="When interest was expressed")

    class Config:
        from_attributes = True


class MemberInterest(BaseModel):
    """
    Member interest with associated listing information.

    Used when listing a member's interests.
    """

    interest_id: int = Field(..., description="Interest record ID")
    listing: ListingTeaser = Field(..., description="Listing information")
    status: str = Field(..., description="Interest status")
    note: Optional[str] = Field(None, description="Buyer note")
    created_at: datetime = Field(..., description="When interest was expressed")
    updated_at: datetime = Field(..., description="Last updated")

    class Config:
        from_attributes = True
