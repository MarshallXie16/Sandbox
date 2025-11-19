"""
Engagement endpoints for Facilitator API.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.models.enums import EngagementStatus
from app.schemas import (
    EngagementCreate,
    EngagementResponse,
    EngagementSetStatus,
    EngagementSummary,
    SuccessResponse,
)
from app.services import EngagementService

router = APIRouter(prefix="/facilitator/engagements", tags=["engagements"])


@router.post("", response_model=EngagementResponse, status_code=201)
async def create_engagement(
    data: EngagementCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new facilitator engagement."""
    service = EngagementService(db)
    engagement = await service.create_engagement(data, actor=api_key[:8])
    return engagement


@router.get("", response_model=List[EngagementResponse])
async def list_engagements(
    status: Optional[EngagementStatus] = Query(None),
    seller_contact_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """List engagements with optional filters."""
    service = EngagementService(db)
    engagements = await service.list_engagements(
        status=status,
        seller_contact_id=seller_contact_id,
        skip=skip,
        limit=limit
    )
    return engagements


@router.get("/{engagement_id}", response_model=EngagementResponse)
async def get_engagement(
    engagement_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get engagement by ID."""
    service = EngagementService(db)
    engagement = await service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    return engagement


@router.get("/{engagement_id}/summary", response_model=EngagementSummary)
async def get_engagement_summary(
    engagement_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get engagement with all related entities."""
    service = EngagementService(db)
    engagement = await service.get_engagement_with_relations(engagement_id)
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    return engagement


@router.post("/{engagement_id}/activate", response_model=EngagementResponse)
async def activate_engagement(
    engagement_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Activate an engagement (transition from DRAFT to ACTIVE)."""
    service = EngagementService(db)
    try:
        engagement = await service.activate_engagement(engagement_id, actor=api_key[:8])
        return engagement
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{engagement_id}/set-status", response_model=EngagementResponse)
async def set_engagement_status(
    engagement_id: int,
    data: EngagementSetStatus,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Change engagement status."""
    service = EngagementService(db)
    try:
        engagement = await service.set_status(
            engagement_id,
            data.status,
            notes=data.notes,
            actor=api_key[:8]
        )
        return engagement
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
