"""
Offer endpoints for Facilitator API.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.schemas import OfferCreate, OfferResponse, OfferSetStatus, OfferMarkFee
from app.services import OfferService

router = APIRouter(tags=["offers"])


@router.post("/facilitator/engagements/{engagement_id}/offers", response_model=OfferResponse, status_code=201)
async def create_offer(
    engagement_id: int,
    data: OfferCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Record an offer from an introduced buyer."""
    service = OfferService(db)
    try:
        offer = await service.create_offer(engagement_id, data, actor=api_key[:8])
        return offer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/facilitator/engagements/{engagement_id}/offers", response_model=List[OfferResponse])
async def list_offers(
    engagement_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """List all offers for an engagement."""
    service = OfferService(db)
    return await service.list_by_engagement(engagement_id, skip, limit)


@router.post("/facilitator/offers/{offer_id}/set-status", response_model=OfferResponse)
async def set_offer_status(
    offer_id: int,
    data: OfferSetStatus,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update offer status."""
    service = OfferService(db)
    try:
        offer = await service.set_status(offer_id, data.status, notes=data.notes, actor=api_key[:8])
        return offer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/facilitator/offers/{offer_id}/mark-fee", response_model=OfferResponse)
async def mark_offer_fee(
    offer_id: int,
    data: OfferMarkFee,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Mark offer fee as invoiced/paid."""
    service = OfferService(db)
    try:
        offer = await service.mark_offer_fee(
            offer_id, invoiced=data.invoiced, paid=data.paid, actor=api_key[:8]
        )
        return offer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
