"""
Repository for Exit Ready event database operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ExitReadyEvent
from app.core.logging import get_logger

logger = get_logger(__name__)


class EventRepository:
    """Repository for Exit Ready event/audit log data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, event_data: Dict[str, Any]) -> ExitReadyEvent:
        """
        Create a new event.

        Args:
            event_data: Dictionary of event attributes

        Returns:
            Created ExitReadyEvent instance
        """
        event = ExitReadyEvent(**event_data)
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        logger.debug(
            f"Created event {event.event_type} for case {event.case_id} "
            f"by {event.actor or 'system'}"
        )
        return event

    async def get_by_id(self, event_id: int) -> Optional[ExitReadyEvent]:
        """
        Get an event by ID.

        Args:
            event_id: Event ID

        Returns:
            ExitReadyEvent or None if not found
        """
        query = select(ExitReadyEvent).where(ExitReadyEvent.id == event_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_case_id(
        self,
        case_id: int,
        limit: Optional[int] = None
    ) -> List[ExitReadyEvent]:
        """
        Get all events for a case.

        Args:
            case_id: Case ID
            limit: Maximum number of events to return

        Returns:
            List of ExitReadyEvent instances
        """
        query = select(ExitReadyEvent).where(
            ExitReadyEvent.case_id == case_id
        ).order_by(ExitReadyEvent.created_at.desc())

        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_event_type(
        self,
        event_type: str,
        case_id: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[ExitReadyEvent]:
        """
        Get events by type.

        Args:
            event_type: Event type to filter by
            case_id: Optional case ID filter
            limit: Maximum number of events to return

        Returns:
            List of ExitReadyEvent instances
        """
        filters = [ExitReadyEvent.event_type == event_type]

        if case_id is not None:
            filters.append(ExitReadyEvent.case_id == case_id)

        query = select(ExitReadyEvent).where(
            and_(*filters)
        ).order_by(ExitReadyEvent.created_at.desc())

        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_recent_events(
        self,
        limit: int = 100,
        case_id: Optional[int] = None
    ) -> List[ExitReadyEvent]:
        """
        Get recent events across all cases or for a specific case.

        Args:
            limit: Maximum number of events to return
            case_id: Optional case ID filter

        Returns:
            List of ExitReadyEvent instances
        """
        query = select(ExitReadyEvent)

        if case_id is not None:
            query = query.where(ExitReadyEvent.case_id == case_id)

        query = query.order_by(
            ExitReadyEvent.created_at.desc()
        ).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def log_status_change(
        self,
        case_id: int,
        from_status: str,
        to_status: str,
        actor: Optional[str] = None
    ) -> ExitReadyEvent:
        """
        Log a status change event.

        Args:
            case_id: Case ID
            from_status: Previous status
            to_status: New status
            actor: Who triggered the change

        Returns:
            Created ExitReadyEvent
        """
        return await self.create({
            "case_id": case_id,
            "event_type": "status_changed",
            "payload": {
                "from_status": from_status,
                "to_status": to_status,
                "timestamp": datetime.utcnow().isoformat(),
            },
            "actor": actor or "system",
        })

    async def log_custom_event(
        self,
        case_id: int,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        actor: Optional[str] = None
    ) -> ExitReadyEvent:
        """
        Log a custom event.

        Args:
            case_id: Case ID
            event_type: Event type
            payload: Event payload
            actor: Who triggered the event

        Returns:
            Created ExitReadyEvent
        """
        return await self.create({
            "case_id": case_id,
            "event_type": event_type,
            "payload": payload,
            "actor": actor or "system",
        })

    async def get_event_type_stats(self) -> List[Dict[str, Any]]:
        """
        Get statistics by event type.

        Returns:
            List of dictionaries with event_type, count, last_occurrence
        """
        query = select(
            ExitReadyEvent.event_type,
            func.count(ExitReadyEvent.id).label("count"),
            func.max(ExitReadyEvent.created_at).label("last_occurrence")
        ).group_by(ExitReadyEvent.event_type)

        result = await self.session.execute(query)

        stats = []
        for event_type, count, last_occurrence in result.all():
            stats.append({
                "event_type": event_type,
                "count": count,
                "last_occurrence": last_occurrence,
            })

        return stats
