"""
Repository for Activity operations.
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crm import Activity
from app.core.base_repository import BaseRepository


class ActivitiesRepository(BaseRepository[Activity]):
    """Repository for managing activities."""

    def __init__(self, session: AsyncSession):
        super().__init__(Activity, session)

    async def get_by_contact(
        self, contact_id: int, limit: int = 100
    ) -> list[Activity]:
        """
        Get activities for a contact.

        Args:
            contact_id: Contact ID
            limit: Maximum results

        Returns:
            List of activities
        """
        result = await self.session.execute(
            select(Activity)
            .where(Activity.contact_id == contact_id)
            .order_by(Activity.occurred_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_deal(self, deal_id: int, limit: int = 100) -> list[Activity]:
        """
        Get activities for a deal.

        Args:
            deal_id: Deal ID
            limit: Maximum results

        Returns:
            List of activities
        """
        result = await self.session.execute(
            select(Activity)
            .where(Activity.deal_id == deal_id)
            .order_by(Activity.occurred_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_activity(
        self,
        activity_type: str,
        contact_id: Optional[int] = None,
        deal_id: Optional[int] = None,
        subject: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Activity:
        """
        Create a new activity.

        Args:
            activity_type: Type of activity
            contact_id: Associated contact ID
            deal_id: Associated deal ID
            subject: Activity subject
            description: Activity description
            metadata: Additional metadata

        Returns:
            Created activity
        """
        return await self.create(
            activity_type=activity_type,
            contact_id=contact_id,
            deal_id=deal_id,
            subject=subject,
            description=description,
            metadata=metadata,
            occurred_at=datetime.utcnow(),
        )

    async def get_recent_by_contact(
        self, contact_id: int, days: int = 30, limit: int = 10
    ) -> list[Activity]:
        """
        Get recent activities for a contact within specified days.

        Args:
            contact_id: Contact ID
            days: Number of days to look back
            limit: Maximum results

        Returns:
            List of recent activities
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        result = await self.session.execute(
            select(Activity)
            .where(
                Activity.contact_id == contact_id, Activity.occurred_at >= cutoff_date
            )
            .order_by(Activity.occurred_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
