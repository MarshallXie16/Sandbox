"""
Service for engagement tracking and scoring.
"""

from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import ContactsRepository, ActivitiesRepository
from app.schemas.engagement import EngagementSummary, EngagementEvent
from app.core.logging import get_logger

logger = get_logger(__name__)


class EngagementService:
    """
    Service for tracking member engagement.

    For now, uses CRM activities and contact details.
    Future: Can integrate with indie-engagement-tracker API.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.contacts_repo = ContactsRepository(session)
        self.activities_repo = ActivitiesRepository(session)

    async def get_engagement_summary(self, contact_id: int) -> Optional[EngagementSummary]:
        """
        Get engagement summary for a contact.

        Args:
            contact_id: Contact ID

        Returns:
            Engagement summary or None if contact not found
        """
        logger.info(f"Getting engagement summary for contact: {contact_id}")

        # Get contact
        contact = await self.contacts_repo.get_by_id(contact_id)
        if not contact:
            logger.warning(f"Contact {contact_id} not found")
            return None

        # Get engagement score from contact details or calculate
        engagement_score = self._get_engagement_score(contact)

        # Get recent activities
        recent_activities = await self.activities_repo.get_recent_by_contact(
            contact_id, days=30, limit=10
        )

        # Convert to engagement events
        recent_events = [
            self._activity_to_event(activity) for activity in recent_activities
        ]

        # Calculate stats
        total_events = len(recent_activities)
        last_activity_date = (
            recent_activities[0].occurred_at if recent_activities else None
        )

        # Count event types (stubbed for now)
        email_opens = sum(
            1 for a in recent_activities if a.activity_type == "email_open"
        )
        link_clicks = sum(
            1 for a in recent_activities if a.activity_type == "link_click"
        )
        form_submissions = sum(
            1 for a in recent_activities if a.activity_type == "form_submit"
        )

        return EngagementSummary(
            engagement_score=engagement_score,
            total_events=total_events,
            recent_events=recent_events,
            last_activity_date=last_activity_date,
            email_opens=email_opens,
            link_clicks=link_clicks,
            form_submissions=form_submissions,
        )

    def _get_engagement_score(self, contact) -> int:
        """
        Get or calculate engagement score.

        Args:
            contact: Contact model

        Returns:
            Engagement score (0-100)
        """
        # Check if score exists in contact details
        if contact.details and "engagement_score" in contact.details:
            return int(contact.details["engagement_score"])

        # Simple calculation based on activity count (stub)
        # In production, this would use indie-engagement-tracker
        return 50  # Default middle score

    def _activity_to_event(self, activity) -> EngagementEvent:
        """
        Convert Activity model to EngagementEvent schema.

        Args:
            activity: Activity model

        Returns:
            EngagementEvent schema
        """
        return EngagementEvent(
            event_type=activity.activity_type,
            occurred_at=activity.occurred_at,
            subject=activity.subject,
            description=activity.description,
            metadata=activity.metadata,
        )
