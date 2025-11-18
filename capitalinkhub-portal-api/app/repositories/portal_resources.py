"""
Repository for PortalResource operations.
"""

from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portal import PortalResource
from app.core.base_repository import BaseRepository


class PortalResourcesRepository(BaseRepository[PortalResource]):
    """Repository for managing portal resources."""

    def __init__(self, session: AsyncSession):
        super().__init__(PortalResource, session)

    async def get_by_slug(self, slug: str) -> Optional[PortalResource]:
        """
        Get resource by slug.

        Args:
            slug: Resource slug

        Returns:
            PortalResource or None
        """
        result = await self.session.execute(
            select(PortalResource).where(PortalResource.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_active_resources(
        self,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        is_gated: Optional[bool] = None,
    ) -> list[PortalResource]:
        """
        Get active resources with optional filters.

        Args:
            category: Filter by category
            resource_type: Filter by type
            is_gated: Filter by gated status

        Returns:
            List of resources
        """
        query = select(PortalResource).where(PortalResource.is_active == True)

        if category:
            query = query.where(PortalResource.category == category)
        if resource_type:
            query = query.where(PortalResource.resource_type == resource_type)
        if is_gated is not None:
            query = query.where(PortalResource.is_gated == is_gated)

        query = query.order_by(PortalResource.created_at.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def increment_download_count(self, resource_id: int) -> Optional[PortalResource]:
        """
        Increment the download count for a resource.

        Args:
            resource_id: Resource ID

        Returns:
            Updated resource or None
        """
        resource = await self.get_by_id(resource_id)
        if resource:
            new_count = resource.download_count + 1
            return await self.update_by_id(resource_id, download_count=new_count)
        return None

    async def create_resource(
        self,
        slug: str,
        title: str,
        category: str,
        resource_type: str,
        description: Optional[str] = None,
        file_url: Optional[str] = None,
        file_size: Optional[int] = None,
        is_gated: bool = True,
        metadata: Optional[dict] = None,
    ) -> PortalResource:
        """
        Create a new resource.

        Args:
            slug: Unique slug
            title: Resource title
            category: Category (buyer, seller, general)
            resource_type: Type (pdf, template, video, etc.)
            description: Description
            file_url: External file URL
            file_size: File size in bytes
            is_gated: Whether login is required
            metadata: Additional metadata

        Returns:
            Created resource
        """
        return await self.create(
            slug=slug,
            title=title,
            description=description,
            category=category,
            resource_type=resource_type,
            file_url=file_url,
            file_size=file_size,
            is_gated=is_gated,
            is_active=True,
            download_count=0,
            metadata=metadata or {},
        )
