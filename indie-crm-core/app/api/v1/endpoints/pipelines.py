"""Pipeline and Stage API endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.repositories.pipeline import PipelineRepository, StageRepository
from app.schemas.pipeline import (
    PipelineCreate,
    PipelineUpdate,
    PipelineResponse,
    StageCreate,
    StageUpdate,
    StageResponse,
)
from app.models.pipeline import PipelineType

router = APIRouter()


# Pipeline Endpoints
@router.get("/", response_model=List[PipelineResponse])
def list_pipelines(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[PipelineType] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """
    List pipelines with optional filtering.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **type**: Filter by pipeline type (seller/buyer)
    - **is_active**: Filter by active status
    """
    repo = PipelineRepository(db)

    filters = {}
    if type:
        filters["type"] = type
    if is_active is not None:
        filters["is_active"] = is_active

    pipelines = repo.get_multi(skip=skip, limit=limit, filters=filters)
    return pipelines


@router.get("/{pipeline_id}", response_model=PipelineResponse)
def get_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    """Get a specific pipeline by ID with all its stages"""
    repo = PipelineRepository(db)
    pipeline = repo.get(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline


@router.post("/", response_model=PipelineResponse, status_code=201)
def create_pipeline(pipeline_in: PipelineCreate, db: Session = Depends(get_db)):
    """Create a new pipeline"""
    repo = PipelineRepository(db)
    pipeline = repo.create(pipeline_in.model_dump())
    return pipeline


@router.put("/{pipeline_id}", response_model=PipelineResponse)
def update_pipeline(
    pipeline_id: int,
    pipeline_in: PipelineUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing pipeline"""
    repo = PipelineRepository(db)

    if not repo.get(pipeline_id):
        raise HTTPException(status_code=404, detail="Pipeline not found")

    update_data = pipeline_in.model_dump(exclude_unset=True)
    pipeline = repo.update(pipeline_id, update_data)
    return pipeline


@router.delete("/{pipeline_id}", status_code=204)
def delete_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    """Delete a pipeline"""
    repo = PipelineRepository(db)
    deleted = repo.delete(pipeline_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return None


# Stage Endpoints
@router.get("/{pipeline_id}/stages", response_model=List[StageResponse])
def list_stages_for_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    """Get all stages for a specific pipeline"""
    # Verify pipeline exists
    pipeline_repo = PipelineRepository(db)
    if not pipeline_repo.get(pipeline_id):
        raise HTTPException(status_code=404, detail="Pipeline not found")

    stage_repo = StageRepository(db)
    stages = stage_repo.get_by_pipeline(pipeline_id)
    return stages


@router.post("/stages", response_model=StageResponse, status_code=201)
def create_stage(stage_in: StageCreate, db: Session = Depends(get_db)):
    """Create a new stage in a pipeline"""
    # Verify pipeline exists
    pipeline_repo = PipelineRepository(db)
    if not pipeline_repo.get(stage_in.pipeline_id):
        raise HTTPException(status_code=404, detail="Pipeline not found")

    stage_repo = StageRepository(db)
    stage = stage_repo.create(stage_in.model_dump())
    return stage


@router.put("/stages/{stage_id}", response_model=StageResponse)
def update_stage(
    stage_id: int,
    stage_in: StageUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing stage"""
    repo = StageRepository(db)

    if not repo.get(stage_id):
        raise HTTPException(status_code=404, detail="Stage not found")

    update_data = stage_in.model_dump(exclude_unset=True)
    stage = repo.update(stage_id, update_data)
    return stage


@router.delete("/stages/{stage_id}", status_code=204)
def delete_stage(stage_id: int, db: Session = Depends(get_db)):
    """Delete a stage"""
    repo = StageRepository(db)
    deleted = repo.delete(stage_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Stage not found")
    return None
