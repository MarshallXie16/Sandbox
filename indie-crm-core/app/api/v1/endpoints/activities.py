"""Activity API endpoints"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.repositories.activity import ActivityRepository
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityResponse
from app.models.activity import ActivityType

router = APIRouter()


@router.get("/", response_model=List[ActivityResponse])
def list_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[ActivityType] = None,
    owner_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    List activities with optional filtering.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **type**: Filter by activity type
    - **owner_id**: Filter by owner
    """
    repo = ActivityRepository(db)

    filters = {}
    if type:
        filters["type"] = type
    if owner_id:
        filters["owner_id"] = owner_id

    activities = repo.get_multi(skip=skip, limit=limit, filters=filters)
    return activities


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    """Get a specific activity by ID"""
    repo = ActivityRepository(db)
    activity = repo.get(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.post("/", response_model=ActivityResponse, status_code=201)
def create_activity(activity_in: ActivityCreate, db: Session = Depends(get_db)):
    """
    Create a new activity.

    Example request body:
    ```json
    {
        "type": "call",
        "subject": "Initial discovery call",
        "content": "Discussed business goals and acquisition timeline",
        "direction": "outgoing",
        "happened_at": "2025-01-15T14:30:00Z",
        "owner_id": 1,
        "details": {
            "duration_minutes": 30,
            "call_outcome": "Positive - moving to next stage"
        }
    }
    ```
    """
    repo = ActivityRepository(db)
    activity = repo.create(activity_in.model_dump())
    return activity


@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    activity_in: ActivityUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing activity"""
    repo = ActivityRepository(db)

    # Check if activity exists
    if not repo.get(activity_id):
        raise HTTPException(status_code=404, detail="Activity not found")

    # Only include non-None values in update
    update_data = activity_in.model_dump(exclude_unset=True)
    activity = repo.update(activity_id, update_data)
    return activity


@router.delete("/{activity_id}", status_code=204)
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    """Delete an activity"""
    repo = ActivityRepository(db)
    deleted = repo.delete(activity_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Activity not found")
    return None
