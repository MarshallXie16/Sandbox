"""
Pydantic schemas for listing-related API operations.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ListingFilters(BaseModel):
    """Query parameters for filtering listings."""

    industry: Optional[str] = Field(None, description="Filter by industry")
    region: Optional[str] = Field(None, description="Filter by region")
    min_price: Optional[float] = Field(None, description="Minimum asking price")
    max_price: Optional[float] = Field(None, description="Maximum asking price")
    min_revenue: Optional[float] = Field(None, description="Minimum revenue")
    max_revenue: Optional[float] = Field(None, description="Maximum revenue")
    status: Optional[str] = Field(None, description="Deal status filter")
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class ListingTeaser(BaseModel):
    """
    Anonymized listing teaser for browse/search results.

    This contains only non-sensitive information suitable for public display.
    """

    listing_id: int = Field(..., description="Deal/listing ID")
    title: str = Field(..., description="Listing title")
    industry: Optional[str] = Field(None, description="Industry sector")
    region: Optional[str] = Field(None, description="Geographic region (high-level)")
    revenue_range: Optional[str] = Field(None, description="Revenue band (e.g., '$1M-$5M')")
    ebitda_range: Optional[str] = Field(None, description="EBITDA band")
    asking_price_range: Optional[str] = Field(None, description="Asking price range")
    short_description: Optional[str] = Field(None, description="Brief description")
    status: str = Field(..., description="Listing status")
    posted_date: datetime = Field(..., description="When listing was posted")

    class Config:
        from_attributes = True


class ListingDetail(BaseModel):
    """
    Detailed listing information (still anonymized).

    Provides more context than the teaser but still protects seller identity.
    """

    listing_id: int = Field(..., description="Deal/listing ID")
    title: str = Field(..., description="Listing title")
    industry: Optional[str] = Field(None, description="Industry sector")
    region: Optional[str] = Field(None, description="Geographic region")
    revenue_range: Optional[str] = Field(None, description="Revenue band")
    ebitda_range: Optional[str] = Field(None, description="EBITDA band")
    asking_price_range: Optional[str] = Field(None, description="Asking price range")
    description: Optional[str] = Field(None, description="Full description")
    key_highlights: Optional[list[str]] = Field(None, description="Key selling points")
    status: str = Field(..., description="Listing status")
    posted_date: datetime = Field(..., description="Posted date")
    updated_date: datetime = Field(..., description="Last updated")
    company_size: Optional[str] = Field(None, description="Company size range")
    year_established: Optional[int] = Field(None, description="Year business established")

    class Config:
        from_attributes = True
