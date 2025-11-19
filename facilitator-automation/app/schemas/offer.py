"""
Pydantic schemas for Offers.
"""

from datetime import datetime
from typing import Optional, Any, Dict
from decimal import Decimal
from pydantic import Field, field_validator

from app.schemas.base import BaseSchema, TimestampMixin
from app.models.enums import OfferStatus


class OfferBase(BaseSchema):
    """Base offer schema with common fields."""

    buyer_intro_id: int = Field(..., description="ID of the introduced buyer making the offer")
    offer_date: datetime = Field(..., description="Date the offer was made")
    headline_price: Decimal = Field(..., description="Headline offer price")
    currency: str = Field(default="CAD", description="Currency code (ISO 4217)")
    structure: Optional[Dict[str, Any]] = Field(
        None,
        description="Deal structure (e.g., cash, earnout, vendor takeback)"
    )
    notes: Optional[str] = Field(None, description="Notes about the offer")

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        if len(v) != 3:
            raise ValueError("Currency must be 3-letter ISO code")
        return v.upper()


class OfferCreate(OfferBase):
    """Schema for creating a new offer."""

    offer_fee_amount: Optional[Decimal] = Field(
        None,
        description="Offer fee amount (defaults to engagement's offer_fee_fixed)"
    )


class OfferUpdate(BaseSchema):
    """Schema for updating an offer."""

    status: Optional[OfferStatus] = None
    headline_price: Optional[Decimal] = None
    structure: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class OfferSetStatus(BaseSchema):
    """Schema for setting offer status."""

    status: OfferStatus = Field(..., description="New status")
    notes: Optional[str] = Field(None, description="Notes about the status change")


class OfferMarkFee(BaseSchema):
    """Schema for marking offer fee as invoiced/paid."""

    invoiced: Optional[bool] = Field(None, description="Mark as invoiced")
    paid: Optional[bool] = Field(None, description="Mark as paid")


class OfferResponse(OfferBase, TimestampMixin):
    """Schema for offer response."""

    id: int
    engagement_id: int
    status: OfferStatus
    offer_fee_amount: Decimal = Field(..., description="Offer fee amount")
    offer_fee_invoiced: bool = Field(..., description="Whether offer fee has been invoiced")
    offer_fee_paid: bool = Field(..., description="Whether offer fee has been paid")
