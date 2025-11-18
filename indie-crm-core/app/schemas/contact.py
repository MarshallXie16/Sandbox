"""Pydantic schemas for Contact"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.contact import ContactCategory


class ContactBase(BaseModel):
    """Base schema for Contact"""

    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    primary_email: EmailStr
    secondary_email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    whatsapp: Optional[str] = Field(None, max_length=50)
    wechat: Optional[str] = Field(None, max_length=100)
    primary_language: str = Field(default="English", max_length=50)
    category: ContactCategory = ContactCategory.OTHER
    is_active: bool = True
    details: Dict[str, Any] = Field(default_factory=dict)


class ContactCreate(ContactBase):
    """Schema for creating a Contact"""

    pass


class ContactUpdate(BaseModel):
    """Schema for updating a Contact (all fields optional)"""

    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    primary_email: Optional[EmailStr] = None
    secondary_email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    whatsapp: Optional[str] = Field(None, max_length=50)
    wechat: Optional[str] = Field(None, max_length=100)
    primary_language: Optional[str] = Field(None, max_length=50)
    category: Optional[ContactCategory] = None
    is_active: Optional[bool] = None
    details: Optional[Dict[str, Any]] = None


class ContactResponse(ContactBase):
    """Schema for Contact responses"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
