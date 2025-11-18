"""
Database models for the portal API.

Exports:
- CRM models (Contact, Company, Deal, Activity)
- Portal models (PortalMember, PortalInterest, PortalResource)
"""

from app.models.crm import Contact, Company, Deal, Activity
from app.models.portal import PortalMember, PortalInterest, PortalResource

__all__ = [
    # CRM models
    "Contact",
    "Company",
    "Deal",
    "Activity",
    # Portal models
    "PortalMember",
    "PortalInterest",
    "PortalResource",
]