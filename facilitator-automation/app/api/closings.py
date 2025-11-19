"""
Closing endpoints for Facilitator API.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_api_key
from app.schemas import ClosingCreate, ClosingResponse, ClosingMarkInvoiced
from app.services import ClosingService

router = APIRouter(tags=["closings"])


@router.post("/facilitator/engagements/{engagement_id}/closings", response_model=ClosingResponse, status_code=201)
async def record_closing(
    engagement_id: int,
    data: ClosingCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Record a deal closing with an introduced buyer.

    This calculates success fees: 5% of final price with credit for paid offer fees.
    """
    service = ClosingService(db)
    try:
        closing = await service.record_closing(engagement_id, data, actor=api_key[:8])
        return closing
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/facilitator/engagements/{engagement_id}/closings", response_model=ClosingResponse)
async def get_closing(
    engagement_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get closing for an engagement."""
    service = ClosingService(db)
    closing = await service.get_by_engagement(engagement_id)
    if not closing:
        raise HTTPException(status_code=404, detail="No closing found for this engagement")
    return closing


@router.post("/facilitator/closings/{closing_id}/mark-invoiced", response_model=ClosingResponse)
async def mark_closing_invoiced(
    closing_id: int,
    data: ClosingMarkInvoiced,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Mark success fee as invoiced/paid."""
    service = ClosingService(db)
    try:
        closing = await service.mark_invoiced(
            closing_id, invoiced=data.invoiced, paid=data.paid, actor=api_key[:8]
        )
        return closing
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
