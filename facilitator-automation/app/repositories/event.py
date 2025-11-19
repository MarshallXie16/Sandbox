"""
Repository for Events (audit trail).
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FacilitatorEvent, EventType
from app.repositories.base import BaseRepository


class EventRepository(BaseRepository[FacilitatorEvent]):
    """Repository for event operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(FacilitatorEvent, db)

    async def get_by_engagement(
        self,
        engagement_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorEvent]:
        """Get all events for an engagement."""
        return await self.get_all(
            skip=skip,
            limit=limit,
            engagement_id=engagement_id
        )

    async def get_by_buyer_intro(
        self,
        buyer_intro_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorEvent]:
        """Get all events for a buyer intro."""
        return await self.get_all(
            skip=skip,
            limit=limit,
            buyer_intro_id=buyer_intro_id
        )

    async def get_by_offer(
        self,
        offer_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorEvent]:
        """Get all events for an offer."""
        return await self.get_all(
            skip=skip,
            limit=limit,
            offer_id=offer_id
        )

    async def get_by_closing(
        self,
        closing_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorEvent]:
        """Get all events for a closing."""
        return await self.get_all(
            skip=skip,
            limit=limit,
            closing_id=closing_id
        )

    async def get_by_type(
        self,
        event_type: EventType,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorEvent]:
        """Get all events of a specific type."""
        return await self.get_all(
            skip=skip,
            limit=limit,
            event_type=event_type
        )

    async def get_by_date_range(
        self,
        from_date: datetime,
        to_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorEvent]:
        """
        Get events within a date range.

        Args:
            from_date: Start date (inclusive)
            to_date: End date (inclusive)
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of events
        """
        result = await self.db.execute(
            select(self.model)
            .where(
                self.model.created_at >= from_date,
                self.model.created_at <= to_date
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def log_event(
        self,
        event_type: EventType,
        engagement_id: Optional[int] = None,
        buyer_intro_id: Optional[int] = None,
        offer_id: Optional[int] = None,
        closing_id: Optional[int] = None,
        payload: Optional[dict] = None,
        description: Optional[str] = None,
        actor: Optional[str] = None
    ) -> FacilitatorEvent:
        """
        Log a new event.

        Args:
            event_type: Type of event
            engagement_id: Optional engagement ID
            buyer_intro_id: Optional buyer intro ID
            offer_id: Optional offer ID
            closing_id: Optional closing ID
            payload: Optional structured data
            description: Optional human-readable description
            actor: Optional actor (user or system)

        Returns:
            Created event instance
        """
        return await self.create(
            event_type=event_type,
            engagement_id=engagement_id,
            buyer_intro_id=buyer_intro_id,
            offer_id=offer_id,
            closing_id=closing_id,
            payload=payload,
            description=description,
            actor=actor
        )
