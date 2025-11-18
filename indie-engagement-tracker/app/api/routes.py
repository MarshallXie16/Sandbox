"""FastAPI routes for the engagement tracker API."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import get_db, logger
from app.models import EntityType, ScoreHistory
from app.repositories import ScoringProfileRepository, EngagementRepository
from app.scoring import get_scoring_engine
from app.sources import SourceManager
from app.api import schemas

router = APIRouter()


# Health Check
@router.get("/health", tags=["health"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "engagement-tracker"}


# Scoring Profile Endpoints
@router.post(
    "/profiles",
    response_model=schemas.ScoringProfileResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["profiles"],
)
async def create_profile(
    profile: schemas.ScoringProfileCreate, db: Session = Depends(get_db)
) -> schemas.ScoringProfileResponse:
    """Create a new scoring profile."""
    repo = ScoringProfileRepository(db)

    # Check if name already exists
    existing = repo.get_by_name(profile.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Profile with name '{profile.name}' already exists",
        )

    created = repo.create(
        name=profile.name,
        description=profile.description,
        rules=profile.rules,
        is_default=profile.is_default,
    )

    logger.info(f"Created scoring profile: {created.name} (ID: {created.id})")
    return created


@router.get(
    "/profiles", response_model=List[schemas.ScoringProfileResponse], tags=["profiles"]
)
async def list_profiles(db: Session = Depends(get_db)) -> List[schemas.ScoringProfileResponse]:
    """List all scoring profiles."""
    repo = ScoringProfileRepository(db)
    return repo.get_all()


@router.get(
    "/profiles/{profile_id}",
    response_model=schemas.ScoringProfileResponse,
    tags=["profiles"],
)
async def get_profile(
    profile_id: int, db: Session = Depends(get_db)
) -> schemas.ScoringProfileResponse:
    """Get a scoring profile by ID."""
    repo = ScoringProfileRepository(db)
    profile = repo.get_by_id(profile_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    return profile


@router.patch(
    "/profiles/{profile_id}",
    response_model=schemas.ScoringProfileResponse,
    tags=["profiles"],
)
async def update_profile(
    profile_id: int,
    profile: schemas.ScoringProfileUpdate,
    db: Session = Depends(get_db),
) -> schemas.ScoringProfileResponse:
    """Update a scoring profile."""
    repo = ScoringProfileRepository(db)

    updated = repo.update(
        profile_id,
        name=profile.name,
        description=profile.description,
        rules=profile.rules,
        is_default=profile.is_default,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    logger.info(f"Updated scoring profile: {updated.name} (ID: {updated.id})")
    return updated


@router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["profiles"])
async def delete_profile(profile_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a scoring profile."""
    repo = ScoringProfileRepository(db)

    try:
        deleted = repo.delete(profile_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
            )
        logger.info(f"Deleted scoring profile ID: {profile_id}")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Ingestion Endpoints
@router.post("/ingest/run", response_model=schemas.IngestResponse, tags=["ingestion"])
async def run_ingestion(
    request: schemas.IngestRequest, db: Session = Depends(get_db)
) -> schemas.IngestResponse:
    """Trigger event ingestion from all configured sources."""
    logger.info("Starting ingestion...")

    manager = SourceManager(db)
    stats = manager.ingest_from_all_sources(
        since=request.since, limit=request.limit, dry_run=request.dry_run
    )

    logger.info(
        f"Ingestion complete: {stats['total_new']} new, "
        f"{stats['total_duplicates']} duplicates, {stats['total_errors']} errors"
    )

    return schemas.IngestResponse(**stats)


@router.get("/ingest/test-connections", tags=["ingestion"])
async def test_connections(db: Session = Depends(get_db)) -> dict:
    """Test connections to all configured event sources."""
    manager = SourceManager(db)
    results = manager.test_all_connections()

    return {"sources": results, "all_ok": all(results.values())}


# Score Calculation Endpoints
@router.post(
    "/scores/recalculate",
    response_model=schemas.RecalculateResponse,
    tags=["scoring"],
)
async def recalculate_scores(
    request: schemas.RecalculateRequest, db: Session = Depends(get_db)
) -> schemas.RecalculateResponse:
    """Recalculate engagement scores for all entities."""
    logger.info("Starting score recalculation...")

    try:
        engine = get_scoring_engine(db, request.profile_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    entity_type_enum = None
    if request.entity_type:
        try:
            entity_type_enum = EntityType(request.entity_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid entity_type: {request.entity_type}",
            )

    stats = engine.recalculate_all_scores(
        entity_type=entity_type_enum, min_events=request.min_events
    )

    logger.info(f"Recalculation complete: {stats['recalculated']} entities updated")

    return schemas.RecalculateResponse(**stats)


# Score Query Endpoints
@router.get(
    "/scores/top-contacts",
    response_model=schemas.TopContactsResponse,
    tags=["scoring"],
)
async def get_top_contacts(
    limit: int = 50,
    min_score: float = None,
    since: str = None,
    entity_type: str = None,
    db: Session = Depends(get_db),
) -> schemas.TopContactsResponse:
    """Get top engaged contacts/entities."""
    repo = EngagementRepository(db)

    entity_type_enum = None
    if entity_type:
        try:
            entity_type_enum = EntityType(entity_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid entity_type: {entity_type}",
            )

    # Parse since if provided
    since_dt = None
    if since:
        from datetime import datetime

        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid datetime format for 'since'",
            )

    entities = repo.get_top_contacts(
        limit=limit, min_score=min_score, since=since_dt, entity_type=entity_type_enum
    )

    return schemas.TopContactsResponse(entities=entities, total=len(entities))


@router.get(
    "/scores/contact/{external_id}",
    response_model=schemas.EntityDetailResponse,
    tags=["scoring"],
)
async def get_contact_detail(
    external_id: str, entity_type: str = "contact", db: Session = Depends(get_db)
) -> schemas.EntityDetailResponse:
    """Get detailed score information for a specific contact."""
    repo = EngagementRepository(db)

    try:
        entity_type_enum = EntityType(entity_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity_type: {entity_type}",
        )

    entity = repo.get_entity_by_external_id(external_id, entity_type_enum)

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found"
        )

    # Get recent events
    recent_events = repo.get_entity_events(entity.id, limit=50)

    # Get score history
    score_history = (
        db.query(ScoreHistory)
        .filter(ScoreHistory.engagement_entity_id == entity.id)
        .order_by(ScoreHistory.calculated_at.desc())
        .limit(10)
        .all()
    )

    history_data = [
        {
            "score_value": float(h.score_value),
            "calculated_at": h.calculated_at.isoformat(),
            "components": h.score_components,
        }
        for h in score_history
    ]

    return schemas.EntityDetailResponse(
        entity=entity, recent_events=recent_events, score_history=history_data
    )


# Statistics Endpoint
@router.get("/stats", response_model=schemas.StatisticsResponse, tags=["stats"])
async def get_statistics(db: Session = Depends(get_db)) -> schemas.StatisticsResponse:
    """Get overall engagement statistics."""
    repo = EngagementRepository(db)
    stats = repo.get_statistics()
    return schemas.StatisticsResponse(**stats)
