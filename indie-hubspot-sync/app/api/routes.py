"""
FastAPI routes for sync service control API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import get_logger
from app.models.tracking import SyncRun, SyncError, SyncDirection, EntityType
from app.services.sync_service import SyncService

logger = get_logger(__name__)

router = APIRouter()


# Request/Response Models

class SyncRequest(BaseModel):
    """Request model for triggering a sync."""

    entities: List[str] = Field(
        default=["contacts", "companies", "deals"],
        description="List of entity types to sync",
    )
    direction: SyncDirection = Field(
        default=SyncDirection.BIDIRECTIONAL,
        description="Sync direction",
    )
    dry_run: bool = Field(
        default=False,
        description="If true, simulate sync without making changes",
    )


class SyncResponse(BaseModel):
    """Response model for sync operation."""

    sync_run_id: Optional[int] = None
    results: Dict[str, Any]
    message: str


class SyncRunDetail(BaseModel):
    """Detailed information about a sync run."""

    id: int
    started_at: datetime
    finished_at: Optional[datetime]
    status: str
    direction: str
    summary: Optional[Dict[str, Any]]
    errors: List[Dict[str, Any]] = []


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime
    version: str = "1.0.0"


# Routes

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns service status and current timestamp.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
    )


@router.post("/sync/run", response_model=SyncResponse)
async def run_sync(request: SyncRequest):
    """
    Trigger a synchronization run.

    Syncs specified entities in the given direction.

    Args:
        request: Sync configuration

    Returns:
        Sync results and summary
    """
    logger.info(
        "api_sync_requested",
        entities=request.entities,
        direction=request.direction.value,
        dry_run=request.dry_run,
    )

    try:
        sync_service = SyncService()
        results = {}

        # Sync each entity type
        for entity_str in request.entities:
            entity_str = entity_str.lower()

            if entity_str == "contacts":
                results["contacts"] = sync_service.sync_contacts(
                    direction=request.direction,
                    dry_run=request.dry_run,
                )
            elif entity_str == "companies":
                results["companies"] = sync_service.sync_companies(
                    direction=request.direction,
                    dry_run=request.dry_run,
                )
            elif entity_str == "deals":
                results["deals"] = sync_service.sync_deals(
                    direction=request.direction,
                    dry_run=request.dry_run,
                )
            else:
                logger.warning("unknown_entity_type", entity=entity_str)

        # Calculate totals
        total_created = sum(r.get("created", 0) for r in results.values())
        total_updated = sum(r.get("updated", 0) for r in results.values())
        total_errors = sum(r.get("errors", 0) for r in results.values())

        message = (
            f"Sync completed: {total_created} created, "
            f"{total_updated} updated, {total_errors} errors"
        )

        if request.dry_run:
            message = f"DRY RUN: {message}"

        return SyncResponse(
            results=results,
            message=message,
        )

    except Exception as e:
        logger.error("sync_failed_via_api", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync/runs", response_model=List[Dict[str, Any]])
async def list_sync_runs(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
):
    """
    List recent sync runs.

    Args:
        limit: Maximum number of runs to return
        offset: Pagination offset
        db: Database session

    Returns:
        List of sync runs
    """
    runs = (
        db.query(SyncRun)
        .order_by(SyncRun.started_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": run.id,
            "started_at": run.started_at.isoformat(),
            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
            "status": run.status.value,
            "direction": run.direction.value,
            "summary": run.summary,
        }
        for run in runs
    ]


@router.get("/sync/runs/{run_id}", response_model=SyncRunDetail)
async def get_sync_run(run_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific sync run.

    Args:
        run_id: Sync run ID
        db: Database session

    Returns:
        Sync run details including errors
    """
    run = db.query(SyncRun).filter(SyncRun.id == run_id).first()

    if not run:
        raise HTTPException(status_code=404, detail=f"Sync run {run_id} not found")

    # Get errors for this run
    errors = db.query(SyncError).filter(SyncError.sync_run_id == run_id).all()

    import json

    return SyncRunDetail(
        id=run.id,
        started_at=run.started_at,
        finished_at=run.finished_at,
        status=run.status.value,
        direction=run.direction.value,
        summary=json.loads(run.summary) if run.summary else None,
        errors=[
            {
                "id": err.id,
                "entity_type": err.entity_type.value,
                "indie_id": err.indie_id,
                "hubspot_id": err.hubspot_id,
                "error_message": err.error_message,
                "created_at": err.created_at.isoformat(),
            }
            for err in errors
        ],
    )


@router.get("/sync/stats", response_model=Dict[str, Any])
async def get_sync_stats(db: Session = Depends(get_db)):
    """
    Get overall synchronization statistics.

    Returns:
        Statistics about sync operations
    """
    from sqlalchemy import func
    from app.models.tracking import SyncObject

    total_runs = db.query(func.count(SyncRun.id)).scalar()
    successful_runs = (
        db.query(func.count(SyncRun.id))
        .filter(SyncRun.status == "success")
        .scalar()
    )
    total_errors = db.query(func.count(SyncError.id)).scalar()

    # Count synced objects by type
    synced_contacts = (
        db.query(func.count(SyncObject.id))
        .filter(SyncObject.entity_type == EntityType.CONTACT)
        .scalar()
    )
    synced_companies = (
        db.query(func.count(SyncObject.id))
        .filter(SyncObject.entity_type == EntityType.COMPANY)
        .scalar()
    )
    synced_deals = (
        db.query(func.count(SyncObject.id))
        .filter(SyncObject.entity_type == EntityType.DEAL)
        .scalar()
    )

    # Get most recent sync
    last_sync = db.query(SyncRun).order_by(SyncRun.started_at.desc()).first()

    return {
        "total_runs": total_runs,
        "successful_runs": successful_runs,
        "total_errors": total_errors,
        "synced_objects": {
            "contacts": synced_contacts,
            "companies": synced_companies,
            "deals": synced_deals,
            "total": synced_contacts + synced_companies + synced_deals,
        },
        "last_sync": {
            "id": last_sync.id,
            "started_at": last_sync.started_at.isoformat(),
            "status": last_sync.status.value,
            "direction": last_sync.direction.value,
        }
        if last_sync
        else None,
    }
