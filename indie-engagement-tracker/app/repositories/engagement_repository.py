"""Repository for engagement entity and event operations."""
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models import EngagementEntity, EngagementEvent, EntityType


class EngagementRepository:
    """Repository for engagement entity and event database operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def get_entity_by_id(self, entity_id: int) -> Optional[EngagementEntity]:
        """Get engagement entity by ID."""
        return (
            self.db.query(EngagementEntity)
            .filter(EngagementEntity.id == entity_id)
            .first()
        )

    def get_entity_by_external_id(
        self, external_id: str, entity_type: EntityType
    ) -> Optional[EngagementEntity]:
        """Get engagement entity by external ID and type."""
        return (
            self.db.query(EngagementEntity)
            .filter(
                EngagementEntity.external_id == external_id,
                EngagementEntity.entity_type == entity_type,
            )
            .first()
        )

    def get_top_contacts(
        self,
        limit: int = 50,
        min_score: Optional[float] = None,
        since: Optional[datetime] = None,
        entity_type: Optional[EntityType] = None,
    ) -> List[EngagementEntity]:
        """
        Get top engaged entities.

        Args:
            limit: Maximum number of entities to return
            min_score: Minimum score threshold
            since: Only include entities with activity since this date
            entity_type: Filter by entity type

        Returns:
            List of engagement entities ordered by score
        """
        query = self.db.query(EngagementEntity)

        if entity_type:
            query = query.filter(EngagementEntity.entity_type == entity_type)

        if min_score is not None:
            query = query.filter(EngagementEntity.latest_score >= min_score)

        if since:
            query = query.filter(EngagementEntity.last_activity_at >= since)

        query = query.order_by(desc(EngagementEntity.latest_score))
        query = query.limit(limit)

        return query.all()

    def get_entity_events(
        self,
        entity_id: int,
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> List[EngagementEvent]:
        """Get events for an entity."""
        query = self.db.query(EngagementEvent).filter(
            EngagementEvent.engagement_entity_id == entity_id
        )

        if since:
            query = query.filter(EngagementEvent.occurred_at >= since)

        query = query.order_by(desc(EngagementEvent.occurred_at))

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall engagement statistics."""
        total_entities = self.db.query(func.count(EngagementEntity.id)).scalar()
        total_events = self.db.query(func.count(EngagementEvent.id)).scalar()

        avg_score = self.db.query(func.avg(EngagementEntity.latest_score)).scalar()

        # Count by entity type
        by_type = {}
        for entity_type in EntityType:
            count = (
                self.db.query(func.count(EngagementEntity.id))
                .filter(EngagementEntity.entity_type == entity_type)
                .scalar()
            )
            by_type[entity_type.value] = count

        # Recent activity count (last 30 days)
        thirty_days_ago = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        recent_activity = (
            self.db.query(func.count(EngagementEntity.id))
            .filter(EngagementEntity.last_activity_at >= thirty_days_ago)
            .scalar()
        )

        return {
            "total_entities": total_entities,
            "total_events": total_events,
            "average_score": round(float(avg_score or 0), 2),
            "by_entity_type": by_type,
            "active_last_30_days": recent_activity,
        }
