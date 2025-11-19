"""Pydantic schemas for Financial models."""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class FinancialInputBase(BaseModel):
    """Base schema for FinancialInput."""
    year: int
    revenue: Decimal
    cogs: Optional[Decimal] = None
    gross_profit: Optional[Decimal] = None
    operating_expenses: Optional[Decimal] = None
    ebitda: Optional[Decimal] = None
    sde: Optional[Decimal] = None
    net_income: Optional[Decimal] = None


class FinancialInputCreate(FinancialInputBase):
    """Schema for creating a new FinancialInput."""
    project_id: UUID


class FinancialInputResponse(FinancialInputBase):
    """Schema for FinancialInput response."""
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NormalizationEntryBase(BaseModel):
    """Base schema for NormalizationEntry."""
    year: int
    category: str
    description: str
    amount: Decimal
    is_addback: bool


class NormalizationEntryCreate(NormalizationEntryBase):
    """Schema for creating a new NormalizationEntry."""
    project_id: UUID


class NormalizationEntryResponse(NormalizationEntryBase):
    """Schema for NormalizationEntry response."""
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NormalizedFinancialResponse(BaseModel):
    """Schema for NormalizedFinancial response."""
    id: UUID
    project_id: UUID
    year: int
    normalized_revenue: Decimal
    normalized_ebitda: Optional[Decimal]
    normalized_sde: Optional[Decimal]
    normalized_net_income: Optional[Decimal]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
