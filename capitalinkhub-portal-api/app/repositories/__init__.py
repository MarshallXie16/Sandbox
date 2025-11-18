"""
Repository layer for database operations.

Exports:
- CRM repositories (Contacts, Companies, Deals, Activities)
- Portal repositories (PortalMembers, PortalInterests, PortalResources)
"""

from app.repositories.contacts import ContactsRepository
from app.repositories.companies import CompaniesRepository
from app.repositories.deals import DealsRepository
from app.repositories.activities import ActivitiesRepository
from app.repositories.portal_members import PortalMembersRepository
from app.repositories.portal_interests import PortalInterestsRepository
from app.repositories.portal_resources import PortalResourcesRepository

__all__ = [
    "ContactsRepository",
    "CompaniesRepository",
    "DealsRepository",
    "ActivitiesRepository",
    "PortalMembersRepository",
    "PortalInterestsRepository",
    "PortalResourcesRepository",
]
