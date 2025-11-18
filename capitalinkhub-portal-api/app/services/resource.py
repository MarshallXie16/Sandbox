"""
Service for portal resource management.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import PortalResourcesRepository
from app.schemas.resource import ResourceResponse, ResourceListFilters
from app.core.logging import get_logger

logger = get_logger(__name__)


class ResourceService:
    """
    Service for managing downloadable resources.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.resources_repo = PortalResourcesRepository(session)

    async def get_resources(
        self, filters: Optional[ResourceListFilters] = None
    ) -> list[ResourceResponse]:
        """
        Get list of active resources with optional filters.

        Args:
            filters: Optional filters

        Returns:
            List of resources
        """
        logger.info(f"Getting resources with filters: {filters}")

        # Apply filters if provided
        category = filters.category if filters else None
        resource_type = filters.resource_type if filters else None
        is_gated = filters.is_gated if filters else None

        resources = await self.resources_repo.get_active_resources(
            category=category, resource_type=resource_type, is_gated=is_gated
        )

        # Convert to response schemas
        result = [
            ResourceResponse(
                slug=resource.slug,
                title=resource.title,
                description=resource.description,
                category=resource.category,
                resource_type=resource.resource_type,
                file_size=resource.file_size,
                is_gated=resource.is_gated,
                download_count=resource.download_count,
                url=self._get_resource_url(resource),
            )
            for resource in resources
        ]

        logger.info(f"Found {len(result)} resources")
        return result

    async def get_resource_by_slug(self, slug: str) -> Optional[ResourceResponse]:
        """
        Get a single resource by slug.

        Args:
            slug: Resource slug

        Returns:
            Resource response or None
        """
        logger.info(f"Getting resource by slug: {slug}")

        resource = await self.resources_repo.get_by_slug(slug)
        if not resource:
            logger.warning(f"Resource not found: {slug}")
            return None

        # Increment download count
        await self.resources_repo.increment_download_count(resource.id)
        await self.session.commit()

        return ResourceResponse(
            slug=resource.slug,
            title=resource.title,
            description=resource.description,
            category=resource.category,
            resource_type=resource.resource_type,
            file_size=resource.file_size,
            is_gated=resource.is_gated,
            download_count=resource.download_count + 1,  # Reflect updated count
            url=self._get_resource_url(resource),
        )

    def _get_resource_url(self, resource) -> Optional[str]:
        """
        Get download URL for a resource.

        In production, this would generate a signed URL or pre-authenticated URL.
        For now, returns the stored file_url.

        Args:
            resource: PortalResource model

        Returns:
            Download URL or None
        """
        # TODO: Implement signed URL generation for S3/CDN
        # For now, return stored URL
        return resource.file_url
