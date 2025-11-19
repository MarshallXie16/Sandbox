"""
Buyer introduction endpoints for Facilitator API.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.schemas import BuyerIntroCreate, BuyerIntroResponse, BuyerIntroSetStatus
from app.services import BuyerIntroService
from app.integrations import MatchingEngineClient

router = APIRouter(prefix="/facilitator/engagements/{engagement_id}/buyers", tags=["buyers"])


@router.post("", response_model=BuyerIntroResponse, status_code=201)
async def introduce_buyer(
    engagement_id: int,
    data: BuyerIntroCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Introduce a buyer to an engagement."""
    service = BuyerIntroService(db)
    try:
        buyer_intro = await service.introduce_buyer(engagement_id, data, actor=api_key[:8])
        return buyer_intro
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[BuyerIntroResponse])
async def list_buyer_intros(
    engagement_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """List all buyer intros for an engagement."""
    service = BuyerIntroService(db)
    return await service.list_by_engagement(engagement_id, skip, limit)


@router.post("/{buyer_intro_id}/set-status", response_model=BuyerIntroResponse)
async def set_buyer_status(
    engagement_id: int,
    buyer_intro_id: int,
    data: BuyerIntroSetStatus,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update buyer intro status."""
    service = BuyerIntroService(db)
    try:
        buyer_intro = await service.set_status(
            buyer_intro_id, data.status, notes=data.notes, actor=api_key[:8]
        )
        return buyer_intro
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/matching-candidates")
async def get_matching_candidates(
    engagement_id: int,
    listing_id: int = Query(...),
    limit: int = Query(50, ge=1, le=100),
    api_key: str = Depends(verify_api_key)
):
    """Get candidate buyers from matching engine (suggestions only)."""
    client = MatchingEngineClient()
    candidates = await client.get_candidate_buyers(listing_id, limit)
    return {"engagement_id": engagement_id, "candidates": candidates}
