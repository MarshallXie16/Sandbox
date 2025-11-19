"""
Pydantic schemas for Facilitator Engagements.
"""

from datetime import datetime
from typing import Optional, Any, Dict
from decimal import Decimal
from pydantic import Field, field_validator

from app.schemas.base import BaseSchema, TimestampMixin
from app.models.enums import EngagementStatus


class EngagementBase(BaseSchema):
    """Base engagement schema with common fields."""

    seller_contact_id: int = Field(..., description="CRM contact ID for the seller")
    company_id: Optional[int] = Field(None, description="CRM company ID")
    listing_id: Optional[int] = Field(None, description="CRM listing/deal ID")
    offer_fee_fixed: Decimal = Field(default=Decimal("5000.00"), description="Fixed fee at offer stage")
    success_fee_rate: Decimal = Field(default=Decimal("0.05"), description="Success fee rate (0.05 = 5%)")
    currency: str = Field(default="CAD", description="Currency code (ISO 4217)")


class EngagementCreate(EngagementBase):
    """Schema for creating a new engagement."""

    terms: Optional[Dict[str, Any]] = Field(None, description="Additional structured terms")
    notes: Optional[str] = Field(None, description="Notes about the engagement")
    created_by: Optional[str] = Field(None, description="User creating the engagement")

    @field_validator("success_fee_rate")
    @classmethod
    def validate_success_fee_rate(cls, v: Decimal) -> Decimal:
        if not 0 <= v <= 1:
            raise ValueError("Success fee rate must be between 0 and 1")
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        if len(v) != 3:
            raise ValueError("Currency must be 3-letter ISO code")
        return v.upper()


class EngagementUpdate(BaseSchema):
    """Schema for updating an engagement."""

    status: Optional[EngagementStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tail_end_date: Optional[datetime] = None
    offer_fee_fixed: Optional[Decimal] = None
    success_fee_rate: Optional[Decimal] = None
    terms: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class EngagementSetStatus(BaseSchema):
    """Schema for setting engagement status."""

    status: EngagementStatus = Field(..., description="New status")
    notes: Optional[str] = Field(None, description="Notes about the status change")


class EngagementResponse(EngagementBase, TimestampMixin):
    """Schema for engagement response."""

    id: int
    engagement_code: str = Field(..., description="Human-readable engagement code")
    status: EngagementStatus
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tail_end_date: Optional[datetime] = None
    terms: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None

    # Counts (populated by service layer if needed)
    buyer_intro_count: Optional[int] = Field(None, description="Number of introduced buyers")
    offer_count: Optional[int] = Field(None, description="Number of offers")
    closing_count: Optional[int] = Field(None, description="Number of closings")


class EngagementSummary(EngagementResponse):
    """Extended engagement response with related entities."""

    from app.schemas.buyer_intro import BuyerIntroResponse
    from app.schemas.offer import OfferResponse
    from app.schemas.closing import ClosingResponse

    buyer_intros: list["BuyerIntroResponse"] = Field(default_factory=list)
    offers: list["OfferResponse"] = Field(default_factory=list)
    closings: list["ClosingResponse"] = Field(default_factory=list)
