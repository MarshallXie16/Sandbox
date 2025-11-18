"""
Core synchronization service for HubSpot ↔ IndieStack integration.

Implements bidirectional sync with conflict resolution.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db_context
from app.core.logging import get_logger
from app.hubspot.client import HubSpotClient
from app.indie.repository import get_indie_repository, IndieRepository
from app.mappings.engine import MappingEngine
from app.models.tracking import (
    EntityType,
    SyncDirection,
    SyncObject,
    SyncRun,
    SyncError,
    SyncStatus,
)

logger = get_logger(__name__)


class SyncService:
    """
    Orchestrates synchronization between IndieStack and HubSpot.

    Handles:
    - Bidirectional data sync
    - Conflict resolution
    - Error tracking
    - Progress monitoring
    """

    def __init__(
        self,
        hubspot_client: Optional[HubSpotClient] = None,
        indie_repo: Optional[IndieRepository] = None,
        mapping_engine: Optional[MappingEngine] = None,
    ):
        """
        Initialize sync service.

        Args:
            hubspot_client: HubSpot API client
            indie_repo: IndieStack repository
            mapping_engine: Field mapping engine
        """
        self.hubspot = hubspot_client or HubSpotClient()
        self.indie = indie_repo or get_indie_repository()
        self.mapper = mapping_engine or MappingEngine()
        logger.info("sync_service_initialized")

    def sync_contacts(
        self,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Synchronize contacts between IndieStack and HubSpot.

        Args:
            direction: Sync direction
            dry_run: If True, don't make actual changes

        Returns:
            Summary of sync operation
        """
        return self._sync_entity(EntityType.CONTACT, direction, dry_run)

    def sync_companies(
        self,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Synchronize companies."""
        return self._sync_entity(EntityType.COMPANY, direction, dry_run)

    def sync_deals(
        self,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Synchronize deals."""
        return self._sync_entity(EntityType.DEAL, direction, dry_run)

    def sync_all(
        self,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Synchronize all entity types.

        Args:
            direction: Sync direction
            dry_run: If True, don't make actual changes

        Returns:
            Combined summary of all sync operations
        """
        logger.info("starting_full_sync", direction=direction.value, dry_run=dry_run)

        results = {
            "contacts": self.sync_contacts(direction, dry_run),
            "companies": self.sync_companies(direction, dry_run),
            "deals": self.sync_deals(direction, dry_run),
        }

        total_created = sum(r["created"] for r in results.values())
        total_updated = sum(r["updated"] for r in results.values())
        total_errors = sum(r["errors"] for r in results.values())

        summary = {
            "results": results,
            "totals": {
                "created": total_created,
                "updated": total_updated,
                "errors": total_errors,
            },
            "dry_run": dry_run,
        }

        logger.info("full_sync_completed", summary=summary)
        return summary

    def _sync_entity(
        self,
        entity_type: EntityType,
        direction: SyncDirection,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Generic entity synchronization logic.

        Args:
            entity_type: Type of entity to sync
            direction: Sync direction
            dry_run: If True, don't make actual changes

        Returns:
            Summary of sync operation
        """
        with get_db_context() as db:
            # Create sync run record
            sync_run = SyncRun(
                direction=direction,
                status=SyncStatus.RUNNING,
            )
            db.add(sync_run)
            db.commit()
            db.refresh(sync_run)

            logger.info(
                "sync_started",
                entity_type=entity_type.value,
                direction=direction.value,
                sync_run_id=sync_run.id,
                dry_run=dry_run,
            )

            try:
                stats = {
                    "created": 0,
                    "updated": 0,
                    "skipped": 0,
                    "errors": 0,
                }

                # Execute sync based on direction
                if direction == SyncDirection.INDIE_TO_HUBSPOT:
                    stats = self._sync_indie_to_hubspot(entity_type, db, sync_run, dry_run)
                elif direction == SyncDirection.HUBSPOT_TO_INDIE:
                    stats = self._sync_hubspot_to_indie(entity_type, db, sync_run, dry_run)
                elif direction == SyncDirection.BIDIRECTIONAL:
                    # Two-pass sync with conflict resolution
                    stats_indie_to_hs = self._sync_indie_to_hubspot(
                        entity_type, db, sync_run, dry_run
                    )
                    stats_hs_to_indie = self._sync_hubspot_to_indie(
                        entity_type, db, sync_run, dry_run
                    )

                    # Combine stats
                    stats = {
                        "created": stats_indie_to_hs["created"] + stats_hs_to_indie["created"],
                        "updated": stats_indie_to_hs["updated"] + stats_hs_to_indie["updated"],
                        "skipped": stats_indie_to_hs["skipped"] + stats_hs_to_indie["skipped"],
                        "errors": stats_indie_to_hs["errors"] + stats_hs_to_indie["errors"],
                    }

                # Update sync run
                sync_run.finished_at = datetime.utcnow()
                sync_run.status = SyncStatus.SUCCESS if stats["errors"] == 0 else SyncStatus.PARTIAL
                sync_run.summary = json.dumps(stats)
                db.commit()

                logger.info(
                    "sync_completed",
                    entity_type=entity_type.value,
                    sync_run_id=sync_run.id,
                    stats=stats,
                )

                return stats

            except Exception as e:
                logger.error(
                    "sync_failed",
                    entity_type=entity_type.value,
                    sync_run_id=sync_run.id,
                    error=str(e),
                )
                sync_run.finished_at = datetime.utcnow()
                sync_run.status = SyncStatus.FAILED
                db.commit()
                raise

    def _sync_indie_to_hubspot(
        self,
        entity_type: EntityType,
        db: Session,
        sync_run: SyncRun,
        dry_run: bool = False,
    ) -> Dict[str, int]:
        """
        Sync from IndieStack to HubSpot.

        Args:
            entity_type: Type of entity
            db: Database session
            sync_run: Current sync run
            dry_run: If True, don't make actual changes

        Returns:
            Statistics dict
        """
        stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}

        # Get IndieStack records
        indie_records = self._get_indie_records(entity_type)

        logger.info(
            "indie_to_hubspot_sync",
            entity_type=entity_type.value,
            record_count=len(indie_records),
        )

        for indie_record in indie_records:
            indie_id = str(indie_record["id"])

            try:
                # Check if we have a mapping
                sync_obj = (
                    db.query(SyncObject)
                    .filter(
                        SyncObject.entity_type == entity_type,
                        SyncObject.indie_id == indie_id,
                    )
                    .first()
                )

                # Map IndieStack record to HubSpot properties
                hubspot_props = self.mapper.indie_to_hubspot(entity_type, indie_record)

                if not dry_run:
                    if sync_obj and sync_obj.hubspot_id:
                        # Update existing HubSpot object
                        self._update_hubspot_object(entity_type, sync_obj.hubspot_id, hubspot_props)
                        stats["updated"] += 1

                        # Update sync metadata
                        sync_obj.last_synced_at = datetime.utcnow()
                        sync_obj.last_direction = SyncDirection.INDIE_TO_HUBSPOT

                    else:
                        # Create new HubSpot object
                        hubspot_obj = self._create_hubspot_object(entity_type, hubspot_props)
                        hubspot_id = hubspot_obj["id"]
                        stats["created"] += 1

                        # Create or update sync mapping
                        if sync_obj:
                            sync_obj.hubspot_id = hubspot_id
                            sync_obj.last_synced_at = datetime.utcnow()
                            sync_obj.last_direction = SyncDirection.INDIE_TO_HUBSPOT
                        else:
                            sync_obj = SyncObject(
                                entity_type=entity_type,
                                indie_id=indie_id,
                                hubspot_id=hubspot_id,
                                last_synced_at=datetime.utcnow(),
                                last_direction=SyncDirection.INDIE_TO_HUBSPOT,
                            )
                            db.add(sync_obj)

                    db.commit()
                else:
                    # Dry run - just log what would happen
                    action = "update" if (sync_obj and sync_obj.hubspot_id) else "create"
                    logger.info(
                        "dry_run_action",
                        action=action,
                        entity_type=entity_type.value,
                        indie_id=indie_id,
                    )
                    stats["skipped"] += 1

            except Exception as e:
                logger.error(
                    "failed_to_sync_record",
                    entity_type=entity_type.value,
                    indie_id=indie_id,
                    error=str(e),
                )
                stats["errors"] += 1

                # Log error
                error = SyncError(
                    sync_run_id=sync_run.id,
                    entity_type=entity_type,
                    indie_id=indie_id,
                    error_message=str(e),
                    payload=json.dumps(indie_record),
                )
                db.add(error)
                db.commit()

        return stats

    def _sync_hubspot_to_indie(
        self,
        entity_type: EntityType,
        db: Session,
        sync_run: SyncRun,
        dry_run: bool = False,
    ) -> Dict[str, int]:
        """
        Sync from HubSpot to IndieStack.

        Args:
            entity_type: Type of entity
            db: Database session
            sync_run: Current sync run
            dry_run: If True, don't make actual changes

        Returns:
            Statistics dict
        """
        stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}

        # Get HubSpot records
        hubspot_records = self._get_hubspot_records(entity_type)

        logger.info(
            "hubspot_to_indie_sync",
            entity_type=entity_type.value,
            record_count=len(hubspot_records),
        )

        for hubspot_record in hubspot_records:
            hubspot_id = hubspot_record["id"]

            try:
                # Check if we have a mapping
                sync_obj = (
                    db.query(SyncObject)
                    .filter(
                        SyncObject.entity_type == entity_type,
                        SyncObject.hubspot_id == hubspot_id,
                    )
                    .first()
                )

                # Check for conflicts if object exists in both systems
                if sync_obj and sync_obj.indie_id:
                    # Apply conflict resolution
                    should_update = self._should_update_indie(
                        entity_type,
                        sync_obj,
                        hubspot_record,
                    )

                    if not should_update:
                        stats["skipped"] += 1
                        continue

                # Map HubSpot object to IndieStack payload
                indie_payload = self.mapper.hubspot_to_indie(entity_type, hubspot_record)

                if not dry_run:
                    if sync_obj and sync_obj.indie_id:
                        # Update existing IndieStack record
                        self._update_indie_record(entity_type, sync_obj.indie_id, indie_payload)
                        stats["updated"] += 1

                        # Update sync metadata
                        sync_obj.last_synced_at = datetime.utcnow()
                        sync_obj.last_direction = SyncDirection.HUBSPOT_TO_INDIE

                    else:
                        # Create new IndieStack record
                        indie_record = self._create_indie_record(entity_type, indie_payload)
                        indie_id = str(indie_record["id"])
                        stats["created"] += 1

                        # Create or update sync mapping
                        if sync_obj:
                            sync_obj.indie_id = indie_id
                            sync_obj.last_synced_at = datetime.utcnow()
                            sync_obj.last_direction = SyncDirection.HUBSPOT_TO_INDIE
                        else:
                            sync_obj = SyncObject(
                                entity_type=entity_type,
                                indie_id=indie_id,
                                hubspot_id=hubspot_id,
                                last_synced_at=datetime.utcnow(),
                                last_direction=SyncDirection.HUBSPOT_TO_INDIE,
                            )
                            db.add(sync_obj)

                    db.commit()
                else:
                    # Dry run
                    action = "update" if (sync_obj and sync_obj.indie_id) else "create"
                    logger.info(
                        "dry_run_action",
                        action=action,
                        entity_type=entity_type.value,
                        hubspot_id=hubspot_id,
                    )
                    stats["skipped"] += 1

            except Exception as e:
                logger.error(
                    "failed_to_sync_record",
                    entity_type=entity_type.value,
                    hubspot_id=hubspot_id,
                    error=str(e),
                )
                stats["errors"] += 1

                # Log error
                error = SyncError(
                    sync_run_id=sync_run.id,
                    entity_type=entity_type,
                    hubspot_id=hubspot_id,
                    error_message=str(e),
                    payload=json.dumps(hubspot_record),
                )
                db.add(error)
                db.commit()

        return stats

    def _should_update_indie(
        self,
        entity_type: EntityType,
        sync_obj: SyncObject,
        hubspot_record: Dict[str, Any],
    ) -> bool:
        """
        Determine if IndieStack record should be updated based on conflict resolution.

        Implements the conflict resolution strategy from settings.

        Args:
            entity_type: Type of entity
            sync_obj: Sync object with metadata
            hubspot_record: HubSpot record

        Returns:
            True if should update, False to skip
        """
        strategy = settings.sync_conflict_resolution

        if strategy == "indie_wins":
            # IndieStack always wins - never update from HubSpot if exists in both
            return False

        elif strategy == "hubspot_wins":
            # HubSpot always wins
            return True

        elif strategy == "newest_wins":
            # Compare timestamps
            hubspot_updated = hubspot_record.get("properties", {}).get("lastmodifieddate")
            if not hubspot_updated:
                return False

            hubspot_dt = datetime.fromtimestamp(int(hubspot_updated) / 1000)

            # Get IndieStack record to check timestamp
            indie_record = self._get_indie_record(entity_type, sync_obj.indie_id)
            if not indie_record:
                return True

            indie_updated = indie_record.get("updated_at")
            if isinstance(indie_updated, str):
                indie_dt = datetime.fromisoformat(indie_updated.replace("Z", "+00:00"))
            else:
                indie_dt = indie_updated

            return hubspot_dt > indie_dt

        return True

    # Helper methods for data access

    def _get_indie_records(self, entity_type: EntityType) -> List[Dict[str, Any]]:
        """Get all records of entity type from IndieStack."""
        if entity_type == EntityType.CONTACT:
            return self.indie.get_contacts()
        elif entity_type == EntityType.COMPANY:
            return self.indie.get_companies()
        elif entity_type == EntityType.DEAL:
            return self.indie.get_deals()
        return []

    def _get_indie_record(self, entity_type: EntityType, indie_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific record from IndieStack."""
        if entity_type == EntityType.CONTACT:
            return self.indie.get_contact(indie_id)
        elif entity_type == EntityType.COMPANY:
            return self.indie.get_company(indie_id)
        elif entity_type == EntityType.DEAL:
            return self.indie.get_deal(indie_id)
        return None

    def _create_indie_record(self, entity_type: EntityType, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a record in IndieStack."""
        if entity_type == EntityType.CONTACT:
            return self.indie.create_contact(data)
        elif entity_type == EntityType.COMPANY:
            return self.indie.create_company(data)
        elif entity_type == EntityType.DEAL:
            return self.indie.create_deal(data)
        raise ValueError(f"Unsupported entity type: {entity_type}")

    def _update_indie_record(
        self,
        entity_type: EntityType,
        indie_id: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a record in IndieStack."""
        if entity_type == EntityType.CONTACT:
            return self.indie.update_contact(indie_id, data)
        elif entity_type == EntityType.COMPANY:
            return self.indie.update_company(indie_id, data)
        elif entity_type == EntityType.DEAL:
            return self.indie.update_deal(indie_id, data)
        raise ValueError(f"Unsupported entity type: {entity_type}")

    def _get_hubspot_records(self, entity_type: EntityType) -> List[Dict[str, Any]]:
        """Get all records of entity type from HubSpot."""
        if entity_type == EntityType.CONTACT:
            response = self.hubspot.get_contacts(limit=100)
        elif entity_type == EntityType.COMPANY:
            response = self.hubspot.get_companies(limit=100)
        elif entity_type == EntityType.DEAL:
            response = self.hubspot.get_deals(limit=100)
        else:
            return []

        return response.get("results", [])

    def _create_hubspot_object(
        self,
        entity_type: EntityType,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create an object in HubSpot."""
        if entity_type == EntityType.CONTACT:
            return self.hubspot.create_contact(properties)
        elif entity_type == EntityType.COMPANY:
            return self.hubspot.create_company(properties)
        elif entity_type == EntityType.DEAL:
            return self.hubspot.create_deal(properties)
        raise ValueError(f"Unsupported entity type: {entity_type}")

    def _update_hubspot_object(
        self,
        entity_type: EntityType,
        hubspot_id: str,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update an object in HubSpot."""
        if entity_type == EntityType.CONTACT:
            return self.hubspot.update_contact(hubspot_id, properties)
        elif entity_type == EntityType.COMPANY:
            return self.hubspot.update_company(hubspot_id, properties)
        elif entity_type == EntityType.DEAL:
            return self.hubspot.update_deal(hubspot_id, properties)
        raise ValueError(f"Unsupported entity type: {entity_type}")
