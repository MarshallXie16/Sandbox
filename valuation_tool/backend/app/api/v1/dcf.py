"""API endpoints for DCF valuation."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.dcf_parameter import DCFParameter
from app.models.dcf_cash_flow import DCFCashFlow
from app.schemas.dcf import (
    DCFParameterCreate,
    DCFParameterUpdate,
    DCFParameterResponse,
    DCFCashFlowCreate,
    DCFCashFlowResponse,
    DCFResultResponse,
    DCFComputeRequest
)
from app.services.dcf_engine import compute_dcf_valuation, get_dcf_result

router = APIRouter()


# DCF Parameters
@router.post("/dcf-parameters", response_model=DCFParameterResponse, status_code=201)
async def create_dcf_parameters(
    data: DCFParameterCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create or update DCF parameters for a project."""
    # Delete existing if any
    existing_result = await db.execute(
        select(DCFParameter).where(DCFParameter.project_id == data.project_id)
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        await db.delete(existing)

    params = DCFParameter(**data.model_dump())
    db.add(params)
    await db.flush()
    await db.refresh(params)
    return params


@router.get("/projects/{project_id}/dcf-parameters", response_model=DCFParameterResponse)
async def get_dcf_parameters(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get DCF parameters for a project."""
    result = await db.execute(
        select(DCFParameter).where(DCFParameter.project_id == project_id)
    )
    params = result.scalar_one_or_none()

    if not params:
        raise HTTPException(status_code=404, detail="DCF parameters not found")

    return params


@router.patch("/projects/{project_id}/dcf-parameters", response_model=DCFParameterResponse)
async def update_dcf_parameters(
    project_id: UUID,
    update_data: DCFParameterUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update DCF parameters for a project."""
    result = await db.execute(
        select(DCFParameter).where(DCFParameter.project_id == project_id)
    )
    params = result.scalar_one_or_none()

    if not params:
        raise HTTPException(status_code=404, detail="DCF parameters not found")

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(params, field, value)

    await db.flush()
    await db.refresh(params)
    return params


# DCF Cash Flows
@router.post("/dcf-cash-flows", response_model=DCFCashFlowResponse, status_code=201)
async def create_dcf_cash_flow(
    data: DCFCashFlowCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a projected cash flow for DCF calculation."""
    cash_flow = DCFCashFlow(**data.model_dump())
    db.add(cash_flow)
    await db.flush()
    await db.refresh(cash_flow)
    return cash_flow


@router.get("/projects/{project_id}/dcf-cash-flows", response_model=List[DCFCashFlowResponse])
async def list_dcf_cash_flows(project_id: UUID, db: AsyncSession = Depends(get_db)):
    """List all DCF cash flows for a project."""
    result = await db.execute(
        select(DCFCashFlow)
        .where(DCFCashFlow.project_id == project_id)
        .order_by(DCFCashFlow.year_index)
    )
    cash_flows = result.scalars().all()
    return cash_flows


@router.delete("/dcf-cash-flows/{cash_flow_id}", status_code=204)
async def delete_dcf_cash_flow(cash_flow_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a DCF cash flow."""
    result = await db.execute(
        select(DCFCashFlow).where(DCFCashFlow.id == cash_flow_id)
    )
    cash_flow = result.scalar_one_or_none()

    if not cash_flow:
        raise HTTPException(status_code=404, detail="DCF cash flow not found")

    await db.delete(cash_flow)
    return None


# DCF Computation
@router.post("/compute-dcf", response_model=DCFResultResponse)
async def compute_dcf(
    request: DCFComputeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Compute DCF valuation for a project."""
    try:
        result = await compute_dcf_valuation(db, request.project_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects/{project_id}/dcf-result", response_model=DCFResultResponse)
async def get_dcf_result_endpoint(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get DCF result for a project."""
    try:
        result = await get_dcf_result(db, project_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
