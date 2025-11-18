"""
Pydantic schemas for listing (deal + company) data.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class ListingProfile(BaseModel):
    """
    Listing profile extracted from CRM deal + company data.
    """

    # Deal identifiers
    id: int = Field(..., description="Deal ID from CRM")
    name: str = Field(..., description="Deal/listing name")
    company_id: Optional[int] = Field(None, description="Related company ID")
    company_name: Optional[str] = Field(None, description="Company name")

    # Deal details
    amount: Optional[float] = Field(
        None,
        description="Ask price / deal amount",
        ge=0,
    )
    status: Optional[str] = Field(None, description="Deal status")
    stage: Optional[str] = Field(None, description="Deal stage")

    # Business details
    industry: Optional[str] = Field(None, description="Industry/sector")
    region: Optional[str] = Field(None, description="Geographic region")

    # Financials
    revenue: Optional[float] = Field(None, description="Annual revenue", ge=0)
    ebitda: Optional[float] = Field(None, description="EBITDA", ge=0)

    # Additional info
    deal_size_band: Optional[str] = Field(
        None,
        description="Size classification: micro, small, mid, large, etc.",
    )
    tags: List[str] = Field(default_factory=list, description="Tags/keywords")
    description: Optional[str] = Field(None, description="Listing description")

    class Config:
        from_attributes = True


class ListingListRequest(BaseModel):
    """Request parameters for listing deals."""

    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    status: Optional[str] = Field(None, description="Filter by status")
    industry: Optional[str] = Field(None, description="Filter by industry")
