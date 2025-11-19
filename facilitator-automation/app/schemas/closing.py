"""
Pydantic schemas for Closings.
"""

from datetime import datetime
from typing import Optional, Any, Dict
from decimal import Decimal
from pydantic import Field, field_validator

from app.schemas.base import BaseSchema, TimestampMixin


class ClosingBase(BaseSchema):
    """Base closing schema with common fields."""

    buyer_intro_id: int = Field(
        ...,
        description="ID of the introduced buyer who closed the deal (REQUIRED for success fee)"
    )
    closing_date: datetime = Field(..., description="Date of closing")
    final_price: Decimal = Field(..., description="Final transaction price")
    currency: str = Field(default="CAD", description="Currency code (ISO 4217)")
    final_structure: Optional[Dict[str, Any]] = Field(
        None,
        description="Final deal structure"
    )
    notes: Optional[str] = Field(None, description="Notes about the closing")

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        if len(v) != 3:
            raise ValueError("Currency must be 3-letter ISO code")
        return v.upper()


class ClosingCreate(ClosingBase):
    """Schema for creating a new closing."""

    pass


class ClosingUpdate(BaseSchema):
    """Schema for updating a closing."""

    final_price: Optional[Decimal] = None
    final_structure: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class ClosingMarkInvoiced(BaseSchema):
    """Schema for marking closing as invoiced/paid."""

    invoiced: Optional[bool] = Field(None, description="Mark as invoiced")
    paid: Optional[bool] = Field(None, description="Mark as paid")


class ClosingResponse(ClosingBase, TimestampMixin):
    """Schema for closing response."""

    id: int
    engagement_id: int
    success_fee_rate: Decimal = Field(..., description="Success fee rate applied")
    success_fee_gross_amount: Decimal = Field(..., description="Gross success fee (before credit)")
    offer_fee_credit_amount: Decimal = Field(..., description="Credit for offer fees already paid")
    success_fee_net_amount: Decimal = Field(..., description="Net success fee (after credit)")
    invoiced: bool = Field(..., description="Whether success fee has been invoiced")
    paid: bool = Field(..., description="Whether success fee has been paid")
