"""
Pydantic schemas for Exit Ready cases.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, EmailStr, field_validator

from app.core.workflow import CaseStatus


class CaseBase(BaseModel):
    """Base schema for Exit Ready case."""
    owner_name: str = Field(..., min_length=1, max_length=255)
    owner_email: EmailStr
    company_name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class CaseCreate(CaseBase):
    """Schema for creating a new Exit Ready case."""
    contact_id: Optional[int] = None
    company_id: Optional[int] = None


class CaseUpdate(BaseModel):
    """Schema for updating an Exit Ready case."""
    owner_name: Optional[str] = Field(None, min_length=1, max_length=255)
    owner_email: Optional[EmailStr] = None
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    next_step: Optional[str] = Field(None, max_length=100)


class CaseStatusUpdate(BaseModel):
    """Schema for updating case status."""
    status: CaseStatus
    admin_override: bool = Field(default=False)
    actor: Optional[str] = None


class CaseIntakeData(BaseModel):
    """Schema for intake form data."""
    business_age: Optional[int] = None
    annual_revenue: Optional[float] = None
    profit_margin: Optional[float] = None
    owner_goals: Optional[str] = None
    ideal_timeline: Optional[str] = None
    asking_price: Optional[float] = None
    reason_for_sale: Optional[str] = None
    additional_notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class CaseResponse(CaseBase):
    """Schema for Exit Ready case response."""
    id: int
    case_code: str
    status: str
    contact_id: Optional[int]
    company_id: Optional[int]

    created_at: datetime
    updated_at: datetime

    # Intake
    intake_form_url: Optional[str]
    intake_sent_at: Optional[datetime]
    intake_received_at: Optional[datetime]
    intake_payload: Optional[Dict[str, Any]]

    # Financials & valuation
    normalized_financials: Optional[Dict[str, Any]]
    normalized_financials_last_run_at: Optional[datetime]
    valuation_payload: Optional[Dict[str, Any]]
    valuation_last_run_at: Optional[datetime]

    # Drafts & documents
    drafts: Optional[Dict[str, Any]]
    drafts_generated_at: Optional[datetime]
    report_url: Optional[str]
    teaser_url: Optional[str]
    cim_url: Optional[str]

    # Delivery
    report_ready_at: Optional[datetime]
    delivered_at: Optional[datetime]
    delivery_channel: Optional[str]
    next_step: Optional[str]

    model_config = {"from_attributes": True}


class CaseSummary(BaseModel):
    """Lightweight schema for case listings."""
    id: int
    case_code: str
    status: str
    owner_name: str
    owner_email: str
    company_name: str
    industry: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CaseList(BaseModel):
    """Schema for paginated case list."""
    items: List[CaseSummary]
    total: int
    page: int
    page_size: int
    total_pages: int


class CaseStats(BaseModel):
    """Schema for case statistics."""
    total_cases: int
    by_status: Dict[str, int]
    by_stage: Dict[str, int]
    avg_days_to_complete: Optional[float]
    cases_this_month: int
    cases_this_quarter: int
