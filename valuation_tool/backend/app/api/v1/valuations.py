"""API endpoints for Valuations (Quick and Full)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.schemas.valuation import (
    QuickValuationRequest,
    ValuationSummaryResponse,
    FullValuationRequest,
    FullValuationSummaryResponse
)
from app.services.quick_valuation_engine import compute_quick_valuation, get_valuation_summary
from app.services.full_valuation_engine import compute_full_valuation, get_full_valuation_summary

router = APIRouter()


# Quick Valuation (Market Approach)
@router.post("/quick-valuation", response_model=ValuationSummaryResponse)
async def run_quick_valuation(
    request: QuickValuationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run Quick Valuation (Market Approach using industry multiples)."""
    try:
        summary = await compute_quick_valuation(db, request.project_id, request.method)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects/{project_id}/quick-valuation", response_model=ValuationSummaryResponse)
async def get_quick_valuation(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get Quick Valuation summary for a project."""
    try:
        summary = await get_valuation_summary(db, project_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Full Valuation (Weighted)
@router.post("/full-valuation", response_model=FullValuationSummaryResponse)
async def run_full_valuation(
    request: FullValuationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run Full Valuation (Weighted combination of Market, DCF, and Asset approaches)."""
    try:
        summary = await compute_full_valuation(
            db,
            request.project_id,
            request.weight_market,
            request.weight_dcf,
            request.weight_asset,
            request.asset_value
        )
        return summary
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects/{project_id}/full-valuation", response_model=FullValuationSummaryResponse)
async def get_full_valuation(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get Full Valuation summary for a project."""
    try:
        summary = await get_full_valuation_summary(db, project_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
