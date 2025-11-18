"""
Resource download endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import verify_api_key
from app.services import ResourceService
from app.schemas.resource import ResourceResponse, ResourceListFilters
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get(
    "",
    response_model=list[ResourceResponse],
    dependencies=[Depends(verify_api_key)],
    summary="Get available resources",
    description="List downloadable resources (templates, guides, etc.) with optional filters.",
)
async def get_resources(
    category: Optional[str] = Query(None, description="Filter by category (buyer, seller, general)"),
    resource_type: Optional[str] = Query(None, description="Filter by type (pdf, template, video, etc.)"),
    is_gated: Optional[bool] = Query(None, description="Filter by gated status"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of available resources.

    Resources can be filtered by category, type, and gated status.
    """
    try:
        filters = ResourceListFilters(
            category=category,
            resource_type=resource_type,
            is_gated=is_gated,
        )

        resource_service = ResourceService(db)
        resources = await resource_service.get_resources(filters)

        return resources
    except Exception as e:
        logger.error(f"Error getting resources: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/{slug}",
    response_model=ResourceResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Get resource by slug",
    description="Get a specific resource and increment its download count.",
)
async def get_resource(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a resource by slug.

    Increments the download count when accessed.
    """
    try:
        resource_service = ResourceService(db)
        resource = await resource_service.get_resource_by_slug(slug)

        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource '{slug}' not found",
            )

        return resource
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resource: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
