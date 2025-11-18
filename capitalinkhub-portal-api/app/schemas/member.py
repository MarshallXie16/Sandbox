"""
Pydantic schemas for member-related API operations.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class MemberResolveRequest(BaseModel):
    """Request to resolve/create a portal member mapping."""

    um_user_id: str = Field(..., description="Ultimate Member user ID")
    email: EmailStr = Field(..., description="User email address")
    role: str = Field(..., description="User role: buyer, seller, or both")
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")


class ContactProfile(BaseModel):
    """Contact profile information."""

    id: int = Field(..., description="Contact ID")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    email: Optional[str] = Field(None, description="Primary email")
    phone: Optional[str] = Field(None, description="Phone number")
    title: Optional[str] = Field(None, description="Job title")
    category: Optional[str] = Field(None, description="Contact category")

    class Config:
        from_attributes = True


class CompanyProfile(BaseModel):
    """Company profile information."""

    id: int = Field(..., description="Company ID")
    name: str = Field(..., description="Company name")
    website: Optional[str] = Field(None, description="Company website")
    industry: Optional[str] = Field(None, description="Industry")
    region: Optional[str] = Field(None, description="Geographic region")

    class Config:
        from_attributes = True


class MemberProfile(BaseModel):
    """Full member profile combining contact and company info."""

    member_id: int = Field(..., description="Portal member ID")
    contact_id: int = Field(..., description="CRM contact ID")
    um_user_id: str = Field(..., description="Ultimate Member user ID")
    role: str = Field(..., description="Member role: buyer, seller, both")
    contact: ContactProfile = Field(..., description="Contact profile")
    company: Optional[CompanyProfile] = Field(None, description="Associated company")


class MemberResolveResponse(BaseModel):
    """Response from member resolution."""

    member_id: int = Field(..., description="Portal member ID")
    contact_id: int = Field(..., description="CRM contact ID")
    um_user_id: str = Field(..., description="Ultimate Member user ID")
    role: str = Field(..., description="Member role")
    is_new: bool = Field(..., description="Whether this is a newly created mapping")
    profile: MemberProfile = Field(..., description="Full member profile")
