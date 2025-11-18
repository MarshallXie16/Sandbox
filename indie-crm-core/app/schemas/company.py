"""Pydantic schemas for Company"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class CompanyBase(BaseModel):
    """Base schema for Company"""

    name: str = Field(..., max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=100)
    revenue: Optional[float] = None
    employees: Optional[int] = None
    earnings: Optional[float] = None
    fiscal_year_end: Optional[str] = Field(None, max_length=10)
    founded_year: Optional[int] = None
    recurring_arr: Optional[float] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class CompanyCreate(CompanyBase):
    """Schema for creating a Company"""

    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a Company (all fields optional)"""

    name: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=100)
    revenue: Optional[float] = None
    employees: Optional[int] = None
    earnings: Optional[float] = None
    fiscal_year_end: Optional[str] = Field(None, max_length=10)
    founded_year: Optional[int] = None
    recurring_arr: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class CompanyResponse(CompanyBase):
    """Schema for Company responses"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
