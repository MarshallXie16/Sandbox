"""Deal API endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.repositories.deal import DealRepository
from app.schemas.deal import DealCreate, DealUpdate, DealResponse
from app.models.deal import DealStatus
from app.models.pipeline import PipelineType

router = APIRouter()


@router.get("/", response_model=List[DealResponse])
def list_deals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    pipeline_id: Optional[int] = None,
    stage_id: Optional[int] = None,
    status: Optional[DealStatus] = None,
    pipeline_type: Optional[PipelineType] = None,
    owner_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    List deals with optional filtering.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **pipeline_id**: Filter by pipeline
    - **stage_id**: Filter by stage
    - **status**: Filter by status (open/won/lost)
    - **pipeline_type**: Filter by pipeline type (seller/buyer)
    - **owner_id**: Filter by owner
    """
    repo = DealRepository(db)

    filters = {}
    if pipeline_id:
        filters["pipeline_id"] = pipeline_id
    if stage_id:
        filters["stage_id"] = stage_id
    if status:
        filters["status"] = status
    if pipeline_type:
        filters["pipeline_type"] = pipeline_type
    if owner_id:
        filters["owner_id"] = owner_id

    deals = repo.get_multi(skip=skip, limit=limit, filters=filters)
    return deals


@router.get("/{deal_id}", response_model=DealResponse)
def get_deal(deal_id: int, db: Session = Depends(get_db)):
    """Get a specific deal by ID"""
    repo = DealRepository(db)
    deal = repo.get(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.post("/", response_model=DealResponse, status_code=201)
def create_deal(deal_in: DealCreate, db: Session = Depends(get_db)):
    """
    Create a new deal.

    Example request body:
    ```json
    {
        "name": "Acquisition of Tech Startup",
        "pipeline_type": "buyer",
        "pipeline_id": 2,
        "stage_id": 5,
        "amount": 2500000,
        "currency": "USD",
        "expected_close_date": "2025-06-30",
        "owner_id": 1,
        "status": "open",
        "details": {
            "deal_source": "Referral",
            "competitive_deals": ["Deal A", "Deal B"]
        }
    }
    ```
    """
    repo = DealRepository(db)
    deal = repo.create(deal_in.model_dump())
    return deal


@router.put("/{deal_id}", response_model=DealResponse)
def update_deal(
    deal_id: int,
    deal_in: DealUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing deal"""
    repo = DealRepository(db)

    # Check if deal exists
    if not repo.get(deal_id):
        raise HTTPException(status_code=404, detail="Deal not found")

    # Only include non-None values in update
    update_data = deal_in.model_dump(exclude_unset=True)
    deal = repo.update(deal_id, update_data)
    return deal


@router.delete("/{deal_id}", status_code=204)
def delete_deal(deal_id: int, db: Session = Depends(get_db)):
    """Delete a deal"""
    repo = DealRepository(db)
    deleted = repo.delete(deal_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Deal not found")
    return None
