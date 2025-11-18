"""
HubSpot API client for CRM v3 operations.

Handles authentication, rate limiting, and CRUD operations for
Contacts, Companies, and Deals.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.models.tracking import EntityType

logger = get_logger(__name__)


class HubSpotClient:
    """
    Client for HubSpot CRM v3 API.

    Uses private app token for authentication.
    """

    BASE_URL = "https://api.hubapi.com"

    # Entity type to API endpoint mapping
    ENDPOINTS = {
        EntityType.CONTACT: "/crm/v3/objects/contacts",
        EntityType.COMPANY: "/crm/v3/objects/companies",
        EntityType.DEAL: "/crm/v3/objects/deals",
    }

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize HubSpot client.

        Args:
            api_token: Private app token. If None, uses from settings.
        """
        self.api_token = api_token or settings.hubspot_private_app_token
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        logger.info("hubspot_client_initialized")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    # Contact operations

    def get_contacts(
        self,
        limit: int = 100,
        after: Optional[str] = None,
        properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get list of contacts.

        Args:
            limit: Number of contacts to retrieve (max 100)
            after: Pagination cursor
            properties: List of properties to retrieve

        Returns:
            Response with contacts and pagination info
        """
        return self._get_objects(EntityType.CONTACT, limit, after, properties)

    def get_contacts_since(
        self,
        since: datetime,
        properties: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all contacts modified since a specific timestamp.

        Args:
            since: Timestamp to filter by
            properties: List of properties to retrieve

        Returns:
            List of contact objects
        """
        return self._get_objects_since(EntityType.CONTACT, since, properties)

    def get_contact(self, contact_id: str, properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a specific contact by ID."""
        return self._get_object(EntityType.CONTACT, contact_id, properties)

    def create_contact(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact."""
        return self._create_object(EntityType.CONTACT, properties)

    def update_contact(self, contact_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing contact."""
        return self._update_object(EntityType.CONTACT, contact_id, properties)

    def create_or_update_contact(
        self,
        properties: Dict[str, Any],
        contact_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new contact or update existing one.

        Args:
            properties: Contact properties
            contact_id: If provided, update this contact. Otherwise create new.

        Returns:
            Created or updated contact object
        """
        if contact_id:
            return self.update_contact(contact_id, properties)
        else:
            return self.create_contact(properties)

    # Company operations

    def get_companies(
        self,
        limit: int = 100,
        after: Optional[str] = None,
        properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get list of companies."""
        return self._get_objects(EntityType.COMPANY, limit, after, properties)

    def get_companies_since(
        self,
        since: datetime,
        properties: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Get all companies modified since a specific timestamp."""
        return self._get_objects_since(EntityType.COMPANY, since, properties)

    def get_company(self, company_id: str, properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a specific company by ID."""
        return self._get_object(EntityType.COMPANY, company_id, properties)

    def create_company(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new company."""
        return self._create_object(EntityType.COMPANY, properties)

    def update_company(self, company_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing company."""
        return self._update_object(EntityType.COMPANY, company_id, properties)

    def create_or_update_company(
        self,
        properties: Dict[str, Any],
        company_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new company or update existing one."""
        if company_id:
            return self.update_company(company_id, properties)
        else:
            return self.create_company(properties)

    # Deal operations

    def get_deals(
        self,
        limit: int = 100,
        after: Optional[str] = None,
        properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get list of deals."""
        return self._get_objects(EntityType.DEAL, limit, after, properties)

    def get_deals_since(
        self,
        since: datetime,
        properties: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Get all deals modified since a specific timestamp."""
        return self._get_objects_since(EntityType.DEAL, since, properties)

    def get_deal(self, deal_id: str, properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a specific deal by ID."""
        return self._get_object(EntityType.DEAL, deal_id, properties)

    def create_deal(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deal."""
        return self._create_object(EntityType.DEAL, properties)

    def update_deal(self, deal_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing deal."""
        return self._update_object(EntityType.DEAL, deal_id, properties)

    def create_or_update_deal(
        self,
        properties: Dict[str, Any],
        deal_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new deal or update existing one."""
        if deal_id:
            return self.update_deal(deal_id, properties)
        else:
            return self.create_deal(properties)

    # Association operations

    def create_association(
        self,
        from_type: EntityType,
        from_id: str,
        to_type: EntityType,
        to_id: str,
        association_type_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create an association between two objects.

        Args:
            from_type: Source entity type
            from_id: Source object ID
            to_type: Target entity type
            to_id: Target object ID
            association_type_id: Optional association type ID

        Returns:
            Association response
        """
        from_endpoint = self.ENDPOINTS[from_type].replace("/crm/v3/objects/", "")
        to_endpoint = self.ENDPOINTS[to_type].replace("/crm/v3/objects/", "")

        url = f"/crm/v3/objects/{from_endpoint}/{from_id}/associations/{to_endpoint}/{to_id}"

        if association_type_id:
            url += f"/{association_type_id}"

        try:
            response = self.client.put(url)
            response.raise_for_status()
            logger.info(
                "association_created",
                from_type=from_type.value,
                from_id=from_id,
                to_type=to_type.value,
                to_id=to_id,
            )
            return response.json()
        except httpx.HTTPError as e:
            logger.error(
                "failed_to_create_association",
                error=str(e),
                from_type=from_type.value,
                from_id=from_id,
                to_type=to_type.value,
                to_id=to_id,
            )
            raise

    # Generic CRUD operations

    def _get_objects(
        self,
        entity_type: EntityType,
        limit: int = 100,
        after: Optional[str] = None,
        properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generic method to get objects of any type."""
        endpoint = self.ENDPOINTS[entity_type]
        params = {"limit": min(limit, 100)}

        if after:
            params["after"] = after

        if properties:
            params["properties"] = ",".join(properties)

        try:
            response = self.client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("failed_to_get_objects", entity_type=entity_type.value, error=str(e))
            raise

    def _get_objects_since(
        self,
        entity_type: EntityType,
        since: datetime,
        properties: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Get all objects modified since a timestamp, handling pagination."""
        all_objects = []
        after = None
        batch_size = settings.sync_batch_size

        while True:
            response = self._get_objects(entity_type, limit=batch_size, after=after, properties=properties)

            results = response.get("results", [])
            all_objects.extend(results)

            # Check if we have more pages
            paging = response.get("paging", {})
            after = paging.get("next", {}).get("after")

            if not after:
                break

        # Filter by timestamp (HubSpot doesn't have direct timestamp filter in basic API)
        since_ts = int(since.timestamp() * 1000)
        filtered = [
            obj
            for obj in all_objects
            if obj.get("properties", {}).get("lastmodifieddate")
            and int(obj["properties"]["lastmodifieddate"]) >= since_ts
        ]

        logger.info(
            "objects_fetched_since",
            entity_type=entity_type.value,
            count=len(filtered),
            since=since.isoformat(),
        )

        return filtered

    def _get_object(
        self,
        entity_type: EntityType,
        object_id: str,
        properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generic method to get a single object."""
        endpoint = f"{self.ENDPOINTS[entity_type]}/{object_id}"
        params = {}

        if properties:
            params["properties"] = ",".join(properties)

        try:
            response = self.client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(
                "failed_to_get_object",
                entity_type=entity_type.value,
                object_id=object_id,
                error=str(e),
            )
            raise

    def _create_object(self, entity_type: EntityType, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Generic method to create an object."""
        endpoint = self.ENDPOINTS[entity_type]
        payload = {"properties": properties}

        try:
            response = self.client.post(endpoint, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info(
                "object_created",
                entity_type=entity_type.value,
                object_id=result.get("id"),
            )
            return result
        except httpx.HTTPError as e:
            logger.error(
                "failed_to_create_object",
                entity_type=entity_type.value,
                error=str(e),
                properties=properties,
            )
            raise

    def _update_object(
        self,
        entity_type: EntityType,
        object_id: str,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generic method to update an object."""
        endpoint = f"{self.ENDPOINTS[entity_type]}/{object_id}"
        payload = {"properties": properties}

        try:
            response = self.client.patch(endpoint, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info(
                "object_updated",
                entity_type=entity_type.value,
                object_id=object_id,
            )
            return result
        except httpx.HTTPError as e:
            logger.error(
                "failed_to_update_object",
                entity_type=entity_type.value,
                object_id=object_id,
                error=str(e),
            )
            raise
