"""Pydantic schemas for DCF models."""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class DCFParameterBase(BaseModel):
    """Base schema for DCFParameter."""
    base_metric: str  # 'EBITDA', 'SDE', or 'FCF'
    base_year: int
    discount_rate: Decimal
    projection_years: int
    terminal_method: str  # 'terminal_growth' or 'exit_multiple'
    terminal_growth_rate: Optional[Decimal] = None
    terminal_multiple: Optional[Decimal] = None
    use_explicit_cash_flows: bool = False
    notes: Optional[str] = None


class DCFParameterCreate(DCFParameterBase):
    """Schema for creating DCF parameters."""
    project_id: UUID


class DCFParameterUpdate(BaseModel):
    """Schema for updating DCF parameters."""
    base_metric: Optional[str] = None
    base_year: Optional[int] = None
    discount_rate: Optional[Decimal] = None
    projection_years: Optional[int] = None
    terminal_method: Optional[str] = None
    terminal_growth_rate: Optional[Decimal] = None
    terminal_multiple: Optional[Decimal] = None
    use_explicit_cash_flows: Optional[bool] = None
    notes: Optional[str] = None


class DCFParameterResponse(DCFParameterBase):
    """Schema for DCFParameter response."""
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DCFCashFlowBase(BaseModel):
    """Base schema for DCFCashFlow."""
    year_index: int
    year_label: str
    cash_flow: Decimal


class DCFCashFlowCreate(DCFCashFlowBase):
    """Schema for creating a DCF cash flow."""
    project_id: UUID


class DCFCashFlowResponse(DCFCashFlowBase):
    """Schema for DCFCashFlow response."""
    id: UUID
    project_id: UUID
    discounted_cash_flow: Optional[Decimal]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DCFResultResponse(BaseModel):
    """Schema for DCFResult response."""
    id: UUID
    project_id: UUID
    present_value_of_cash_flows: Decimal
    terminal_value: Decimal
    present_value_of_terminal_value: Decimal
    dcf_equity_value: Decimal
    currency: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DCFComputeRequest(BaseModel):
    """Schema for DCF computation request."""
    project_id: UUID
