"""
Project schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class FinancialInputsCreate(BaseModel):
    """Schema for creating financial inputs"""
    year: int = Field(..., ge=0, le=2, description="Year index (0=current, 1=last year, 2=two years ago)")
    revenue: Optional[float] = Field(None, ge=0)
    net_profit: Optional[float] = None
    ebitda: Optional[float] = None
    total_assets: Optional[float] = Field(None, ge=0)
    total_liabilities: Optional[float] = Field(None, ge=0)


class ProjectCreateQuick(BaseModel):
    """Schema for creating a Quick valuation project"""
    name: str = Field(..., min_length=1, max_length=200)
    industry: Optional[str] = None
    description: Optional[str] = None
    financial_inputs: list[FinancialInputsCreate] = Field(..., min_items=1, max_items=3)


class ProjectCreateStandard(BaseModel):
    """Schema for creating a Standard valuation project"""
    name: str = Field(..., min_length=1, max_length=200)
    industry: Optional[str] = None
    description: Optional[str] = None
    financial_inputs: Optional[list[FinancialInputsCreate]] = Field(default=[], max_items=3)


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: UUID
    name: str
    project_type: str
    industry: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ValuationResponse(BaseModel):
    """Schema for valuation result response"""
    project_id: str
    value_low: float
    value_mid: float
    value_high: float
    primary_method: Optional[str]
