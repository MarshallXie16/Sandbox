"""Event source manager for coordinating multiple sources."""
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.models import EngagementEvent, EngagementEntity, EntityType
from app.sources.base import EventSource, StandardEvent
from app.sources.email_engine_source import EmailEngineSource
from app.sources.indie_crm_source import IndieCrmActivitySource


class SourceManager:
    """
    Manages multiple event sources and coordinates ingestion.

    Handles:
    - Registering and configuring sources
    - Fetching events from all sources
    - Deduplication
    - Storing events in the database
    """

    def __init__(self, db: Session):
        """
        Initialize the source manager.

        Args:
            db: Database session
        """
        self.db = db
        self.sources: List[EventSource] = []
        self._configure_sources()

    def _configure_sources(self) -> None:
        """Configure event sources from settings."""
        # Email Engine Source
        if settings.email_engine_db_url:
            try:
                email_source = EmailEngineSource(
                    {"db_url": settings.email_engine_db_url}
                )
                self.sources.append(email_source)
                logger.info("Registered EmailEngineSource")
            except Exception as e:
                logger.error(f"Failed to register EmailEngineSource: {str(e)}")

        # IndieStack CRM Source
        if settings.indie_crm_db_url or settings.indie_crm_api_url:
            try:
                config = {}
                if settings.indie_crm_db_url:
                    config["db_url"] = settings.indie_crm_db_url
                if settings.indie_crm_api_url:
                    config["api_url"] = settings.indie_crm_api_url
                    config["api_key"] = settings.indie_crm_api_key

                crm_source = IndieCrmActivitySource(config)
                self.sources.append(crm_source)
                logger.info("Registered IndieCrmActivitySource")
            except Exception as e:
                logger.error(f"Failed to register IndieCrmActivitySource: {str(e)}")

        # Future sources can be added here (HubSpot, Sendy, etc.)

        if not self.sources:
            logger.warning("No event sources configured!")

    def test_all_connections(self) -> Dict[str, bool]:
        """
        Test connections to all configured sources.

        Returns:
            Dict mapping source name to connection status
        """
        results = {}
        for source in self.sources:
            results[source.name] = source.test_connection()
        return results

    def ingest_from_all_sources(
        self,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Ingest events from all configured sources.

        Args:
            since: Only ingest events after this datetime
            limit: Maximum events per source
            dry_run: If True, don't save to database

        Returns:
            Statistics about the ingestion
        """
        stats = {
            "sources": {},
            "total_fetched": 0,
            "total_new": 0,
            "total_duplicates": 0,
            "total_errors": 0,
            "dry_run": dry_run,
        }

        for source in self.sources:
            logger.info(f"Ingesting from {source.name}...")

            source_stats = {
                "fetched": 0,
                "new": 0,
                "duplicates": 0,
                "errors": 0,
            }

            try:
                for event in source.fetch_new_events(since=since, limit=limit):
                    source_stats["fetched"] += 1

                    try:
                        if not dry_run:
                            created = self._store_event(event)
                            if created:
                                source_stats["new"] += 1
                            else:
                                source_stats["duplicates"] += 1
                        else:
                            source_stats["new"] += 1

                    except Exception as e:
                        logger.error(
                            f"Error storing event from {source.name}: {str(e)}"
                        )
                        source_stats["errors"] += 1

            except Exception as e:
                logger.error(f"Error fetching from {source.name}: {str(e)}")
                source_stats["errors"] += 1

            stats["sources"][source.name] = source_stats
            stats["total_fetched"] += source_stats["fetched"]
            stats["total_new"] += source_stats["new"]
            stats["total_duplicates"] += source_stats["duplicates"]
            stats["total_errors"] += source_stats["errors"]

            logger.info(
                f"{source.name}: {source_stats['fetched']} fetched, "
                f"{source_stats['new']} new, {source_stats['duplicates']} duplicates"
            )

        if not dry_run:
            self.db.commit()

        return stats

    def _store_event(self, event: StandardEvent) -> bool:
        """
        Store an event in the database.

        Args:
            event: StandardEvent to store

        Returns:
            True if event was created, False if it already exists
        """
        # Check for duplicate (same external_id, event_type, occurred_at, source)
        existing = (
            self.db.query(EngagementEvent)
            .filter(
                EngagementEvent.external_id == event.external_id,
                EngagementEvent.event_type == event.event_type,
                EngagementEvent.source_system == event.source_system,
                EngagementEvent.occurred_at == event.occurred_at,
            )
            .first()
        )

        if existing:
            return False

        # Get or create engagement entity
        entity_type_enum = EntityType(event.entity_type)
        entity = (
            self.db.query(EngagementEntity)
            .filter(
                EngagementEntity.external_id == event.external_id,
                EngagementEntity.entity_type == entity_type_enum,
            )
            .first()
        )

        if not entity:
            entity = EngagementEntity(
                external_id=event.external_id,
                entity_type=entity_type_enum,
                latest_score=0.0,
            )
            self.db.add(entity)
            self.db.flush()  # Get the entity ID

        # Create event
        db_event = EngagementEvent(
            engagement_entity_id=entity.id,
            external_id=event.external_id,
            entity_type=event.entity_type,
            source_system=event.source_system,
            event_type=event.event_type,
            weight=event.weight,
            occurred_at=event.occurred_at,
            metadata=event.metadata,
        )

        self.db.add(db_event)
        return True
