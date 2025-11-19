"""API endpoints for Financial data and normalization."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.financial_input import FinancialInput
from app.models.normalization_entry import NormalizationEntry
from app.schemas.financial import (
    FinancialInputCreate,
    FinancialInputResponse,
    NormalizationEntryCreate,
    NormalizationEntryResponse,
    NormalizedFinancialResponse
)
from app.services.recast_engine import recompute_normalized_financials, get_normalized_financials

router = APIRouter()


# Financial Inputs
@router.post("/financial-inputs", response_model=FinancialInputResponse, status_code=201)
async def create_financial_input(
    data: FinancialInputCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add financial input for a project year."""
    financial_input = FinancialInput(**data.model_dump())
    db.add(financial_input)
    await db.flush()
    await db.refresh(financial_input)
    return financial_input


@router.get("/projects/{project_id}/financial-inputs", response_model=List[FinancialInputResponse])
async def list_financial_inputs(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """List all financial inputs for a project."""
    result = await db.execute(
        select(FinancialInput)
        .where(FinancialInput.project_id == project_id)
        .order_by(FinancialInput.year)
    )
    inputs = result.scalars().all()
    return inputs


# Normalization Entries
@router.post("/normalization-entries", response_model=NormalizationEntryResponse, status_code=201)
async def create_normalization_entry(
    data: NormalizationEntryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a normalization entry (recast adjustment)."""
    entry = NormalizationEntry(**data.model_dump())
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return entry


@router.get("/projects/{project_id}/normalization-entries", response_model=List[NormalizationEntryResponse])
async def list_normalization_entries(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """List all normalization entries for a project."""
    result = await db.execute(
        select(NormalizationEntry)
        .where(NormalizationEntry.project_id == project_id)
        .order_by(NormalizationEntry.year)
    )
    entries = result.scalars().all()
    return entries


@router.delete("/normalization-entries/{entry_id}", status_code=204)
async def delete_normalization_entry(entry_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a normalization entry."""
    result = await db.execute(
        select(NormalizationEntry).where(NormalizationEntry.id == entry_id)
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Normalization entry not found")

    await db.delete(entry)
    return None


# Normalized Financials (Computed)
@router.post("/projects/{project_id}/compute-normalized-financials", response_model=List[NormalizedFinancialResponse])
async def compute_normalized_financials(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Compute normalized financials for a project."""
    try:
        normalized = await recompute_normalized_financials(db, project_id)
        return normalized
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects/{project_id}/normalized-financials", response_model=List[NormalizedFinancialResponse])
async def get_normalized_financials_endpoint(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get normalized financials for a project."""
    normalized = await get_normalized_financials(db, project_id)
    return normalized
