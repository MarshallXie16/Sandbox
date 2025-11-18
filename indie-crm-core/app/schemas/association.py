"""Pydantic schemas for Associations"""
from typing import Optional
from pydantic import BaseModel


# Contact-Company Association
class ContactCompanyCreate(BaseModel):
    """Schema for creating a Contact-Company association"""

    contact_id: int
    company_id: int
    role: Optional[str] = None
    is_primary: bool = False


class ContactCompanyResponse(ContactCompanyCreate):
    """Schema for Contact-Company association responses"""

    id: int

    class Config:
        from_attributes = True


# Contact-Deal Association
class ContactDealCreate(BaseModel):
    """Schema for creating a Contact-Deal association"""

    contact_id: int
    deal_id: int
    role: Optional[str] = None


class ContactDealResponse(ContactDealCreate):
    """Schema for Contact-Deal association responses"""

    id: int

    class Config:
        from_attributes = True


# Company-Deal Association
class CompanyDealCreate(BaseModel):
    """Schema for creating a Company-Deal association"""

    company_id: int
    deal_id: int
    role: Optional[str] = None


class CompanyDealResponse(CompanyDealCreate):
    """Schema for Company-Deal association responses"""

    id: int

    class Config:
        from_attributes = True


# Activity-Contact Association
class ActivityContactCreate(BaseModel):
    """Schema for creating an Activity-Contact association"""

    activity_id: int
    contact_id: int


class ActivityContactResponse(ActivityContactCreate):
    """Schema for Activity-Contact association responses"""

    id: int

    class Config:
        from_attributes = True


# Activity-Company Association
class ActivityCompanyCreate(BaseModel):
    """Schema for creating an Activity-Company association"""

    activity_id: int
    company_id: int


class ActivityCompanyResponse(ActivityCompanyCreate):
    """Schema for Activity-Company association responses"""

    id: int

    class Config:
        from_attributes = True


# Activity-Deal Association
class ActivityDealCreate(BaseModel):
    """Schema for creating an Activity-Deal association"""

    activity_id: int
    deal_id: int


class ActivityDealResponse(ActivityDealCreate):
    """Schema for Activity-Deal association responses"""

    id: int

    class Config:
        from_attributes = True
