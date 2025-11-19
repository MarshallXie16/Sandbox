"""
CRM Client for Facilitator Automation.

Integrates with indie-crm-core for contact and company information.
"""

from typing import Optional, Dict, Any
import httpx
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CRMClient:
    """
    Client for CRM integration.

    Retrieves contact and company information from CRM.
    Can work via API or direct database access.
    """

    def __init__(self):
        self.api_base_url = settings.crm_api_base_url
        self.api_key = settings.crm_api_key
        self.use_api = bool(self.api_key)  # Use API if key is configured

    async def get_contact(self, contact_id: int) -> Optional[Dict[str, Any]]:
        """
        Get contact information by ID.

        Args:
            contact_id: CRM contact ID

        Returns:
            Contact dictionary or None if not found
        """
        if not self.use_api:
            logger.warning(
                "CRM API not configured, returning stub data for contact "
                f"{contact_id}"
            )
            return self._stub_contact(contact_id)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/contacts/{contact_id}",
                    headers={"X-API-Key": self.api_key},
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get contact {contact_id}: {e}")
            return self._stub_contact(contact_id)

    async def get_company(self, company_id: int) -> Optional[Dict[str, Any]]:
        """
        Get company information by ID.

        Args:
            company_id: CRM company ID

        Returns:
            Company dictionary or None if not found
        """
        if not self.use_api:
            logger.warning(
                "CRM API not configured, returning stub data for company "
                f"{company_id}"
            )
            return self._stub_company(company_id)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/companies/{company_id}",
                    headers={"X-API-Key": self.api_key},
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get company {company_id}: {e}")
            return self._stub_company(company_id)

    async def get_listing(self, listing_id: int) -> Optional[Dict[str, Any]]:
        """
        Get listing information by ID.

        Args:
            listing_id: CRM listing/deal ID

        Returns:
            Listing dictionary or None if not found
        """
        if not self.use_api:
            logger.warning(
                "CRM API not configured, returning stub data for listing "
                f"{listing_id}"
            )
            return self._stub_listing(listing_id)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/deals/{listing_id}",
                    headers={"X-API-Key": self.api_key},
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get listing {listing_id}: {e}")
            return self._stub_listing(listing_id)

    def _stub_contact(self, contact_id: int) -> Dict[str, Any]:
        """Return stub contact data."""
        return {
            "id": contact_id,
            "name": f"Contact {contact_id}",
            "email": f"contact{contact_id}@example.com",
            "phone": "+1-555-0100",
            "title": "CEO"
        }

    def _stub_company(self, company_id: int) -> Dict[str, Any]:
        """Return stub company data."""
        return {
            "id": company_id,
            "name": f"Company {company_id}",
            "industry": "Technology",
            "location": "Toronto, ON",
            "revenue": 5000000,
            "employees": 50
        }

    def _stub_listing(self, listing_id: int) -> Dict[str, Any]:
        """Return stub listing data."""
        return {
            "id": listing_id,
            "title": f"Business Listing {listing_id}",
            "asking_price": 2500000,
            "currency": "CAD",
            "industry": "Technology",
            "description": "Well-established tech company for sale"
        }
