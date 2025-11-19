"""
Pydantic schemas for valuation and financials.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class YearlyFinancials(BaseModel):
    """Schema for a single year's financial data."""
    year: int
    revenue: Optional[float] = None
    cogs: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_expenses: Optional[float] = None
    ebitda: Optional[float] = None
    sde: Optional[float] = None  # Seller's Discretionary Earnings
    net_income: Optional[float] = None


class AddbackItem(BaseModel):
    """Schema for financial addback."""
    category: str
    description: str
    amount: float
    year: int


class NormalizedFinancials(BaseModel):
    """Schema for normalized financials."""
    years: List[YearlyFinancials]
    addbacks: Optional[List[AddbackItem]] = None
    notes: Optional[str] = None
    prepared_at: Optional[str] = None
    prepared_by: Optional[str] = None


class ValuationRequest(BaseModel):
    """Schema for valuation request to external engine."""
    business_name: str
    industry: str
    region: Optional[str] = None
    financials: NormalizedFinancials
    metadata: Optional[Dict[str, Any]] = None


class ValuationMultiples(BaseModel):
    """Schema for valuation multiples."""
    sde_multiple_low: Optional[float] = None
    sde_multiple_high: Optional[float] = None
    ebitda_multiple_low: Optional[float] = None
    ebitda_multiple_high: Optional[float] = None
    revenue_multiple_low: Optional[float] = None
    revenue_multiple_high: Optional[float] = None


class ValuationRange(BaseModel):
    """Schema for valuation range."""
    low: float
    mid: float
    high: float
    currency: str = "USD"


class ValuationResponse(BaseModel):
    """Schema for valuation response from external engine."""
    valuation_range: ValuationRange
    multiples: ValuationMultiples
    methodology: Optional[str] = None
    confidence_level: Optional[str] = None  # high, medium, low
    notes: Optional[str] = None
    comparable_sales: Optional[List[Dict[str, Any]]] = None
    assumptions: Optional[Dict[str, Any]] = None
    calculated_at: str


class ValuationStubResponse(BaseModel):
    """Schema for stub valuation response (when external API not available)."""
    valuation_range: ValuationRange
    multiples: ValuationMultiples
    methodology: str = "Stub/Mock Valuation"
    confidence_level: str = "low"
    notes: str = "This is a stub valuation for testing purposes"
    stub_mode: bool = True
