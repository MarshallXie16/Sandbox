"""Pydantic schemas for Valuation models."""
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class ValuationSummaryResponse(BaseModel):
    """Schema for ValuationSummary response."""
    id: UUID
    project_id: UUID
    value_low: Decimal
    value_mid: Decimal
    value_high: Decimal
    method: str
    multiple_low: Optional[Decimal]
    multiple_mid: Optional[Decimal]
    multiple_high: Optional[Decimal]
    base_metric_value: Optional[Decimal]
    base_metric_type: Optional[str]
    currency: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuickValuationRequest(BaseModel):
    """Schema for Quick Valuation request."""
    project_id: UUID
    method: str = "sde_multiple"  # or "ebitda_multiple"


class FullValuationRequest(BaseModel):
    """Schema for Full Valuation request."""
    project_id: UUID
    weight_market: Decimal
    weight_dcf: Decimal
    weight_asset: Decimal
    asset_value: Optional[Decimal] = None

    @field_validator('weight_market', 'weight_dcf', 'weight_asset')
    @classmethod
    def validate_weight_range(cls, v: Decimal) -> Decimal:
        if v < 0 or v > 1:
            raise ValueError('Weight must be between 0 and 1')
        return v


class FullValuationSummaryResponse(BaseModel):
    """Schema for FullValuationSummary response."""
    id: UUID
    project_id: UUID
    market_value_mid: Optional[Decimal]
    dcf_value: Optional[Decimal]
    asset_value: Optional[Decimal]
    weight_market: Decimal
    weight_dcf: Decimal
    weight_asset: Decimal
    final_value_low: Decimal
    final_value_mid: Decimal
    final_value_high: Decimal
    currency: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
