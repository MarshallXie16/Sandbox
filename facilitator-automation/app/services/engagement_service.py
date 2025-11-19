"""
Engagement Service for Facilitator Automation.

Handles business logic for creating and managing facilitator engagements.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models import FacilitatorEngagement, EngagementStatus, EventType
from app.repositories import EngagementRepository, EventRepository
from app.schemas import EngagementCreate, EngagementUpdate, EngagementResponse
from app.services.workflow import WorkflowService
from app.core.logging import get_logger

logger = get_logger(__name__)


class EngagementService:
    """Service for engagement operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.engagement_repo = EngagementRepository(db)
        self.event_repo = EventRepository(db)
        self.workflow_service = WorkflowService()

    async def create_engagement(
        self,
        data: EngagementCreate,
        actor: Optional[str] = None
    ) -> FacilitatorEngagement:
        """
        Create a new facilitator engagement.

        Args:
            data: Engagement creation data
            actor: User creating the engagement

        Returns:
            Created engagement

        Raises:
            ValueError: If validation fails
        """
        # Generate unique engagement code
        engagement_code = await self.engagement_repo.generate_engagement_code()

        # Create engagement
        engagement = await self.engagement_repo.create(
            engagement_code=engagement_code,
            seller_contact_id=data.seller_contact_id,
            company_id=data.company_id,
            listing_id=data.listing_id,
            status=EngagementStatus.DRAFT,
            offer_fee_fixed=data.offer_fee_fixed,
            success_fee_rate=data.success_fee_rate,
            currency=data.currency,
            terms=data.terms,
            notes=data.notes,
            created_by=data.created_by or actor
        )

        # Log event
        await self.event_repo.log_event(
            event_type=EventType.ENGAGEMENT_CREATED,
            engagement_id=engagement.id,
            description=f"Engagement {engagement.engagement_code} created",
            actor=actor,
            payload={
                "engagement_code": engagement.engagement_code,
                "seller_contact_id": data.seller_contact_id,
                "initial_status": EngagementStatus.DRAFT.value
            }
        )

        await self.db.commit()

        logger.info(
            f"Created engagement {engagement.engagement_code} "
            f"(id={engagement.id}) for seller_contact_id={data.seller_contact_id}"
        )

        return engagement

    async def get_engagement(self, engagement_id: int) -> Optional[FacilitatorEngagement]:
        """Get engagement by ID."""
        return await self.engagement_repo.get_by_id(engagement_id)

    async def get_engagement_with_relations(
        self,
        engagement_id: int
    ) -> Optional[FacilitatorEngagement]:
        """Get engagement with all related entities loaded."""
        return await self.engagement_repo.get_with_relations(engagement_id)

    async def list_engagements(
        self,
        status: Optional[EngagementStatus] = None,
        seller_contact_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorEngagement]:
        """List engagements with optional filters."""
        if status:
            return await self.engagement_repo.get_by_status(status, skip, limit)
        elif seller_contact_id:
            return await self.engagement_repo.get_by_seller(seller_contact_id, skip, limit)
        else:
            return await self.engagement_repo.get_all(skip=skip, limit=limit)

    async def activate_engagement(
        self,
        engagement_id: int,
        actor: Optional[str] = None
    ) -> FacilitatorEngagement:
        """
        Activate an engagement (transition from DRAFT to ACTIVE).

        Args:
            engagement_id: Engagement ID
            actor: User performing activation

        Returns:
            Updated engagement

        Raises:
            ValueError: If transition is invalid or engagement not found
        """
        engagement = await self.get_engagement(engagement_id)
        if not engagement:
            raise ValueError(f"Engagement {engagement_id} not found")

        # Validate transition
        self.workflow_service.validate_transition(
            engagement.status,
            EngagementStatus.ACTIVE
        )

        # Update status and set start date
        engagement = await self.engagement_repo.update(
            engagement_id,
            status=EngagementStatus.ACTIVE,
            start_date=datetime.now()
        )

        # Log event
        await self.event_repo.log_event(
            event_type=EventType.ENGAGEMENT_ACTIVATED,
            engagement_id=engagement.id,
            description=f"Engagement {engagement.engagement_code} activated",
            actor=actor,
            payload={
                "old_status": EngagementStatus.DRAFT.value,
                "new_status": EngagementStatus.ACTIVE.value
            }
        )

        await self.db.commit()

        logger.info(f"Activated engagement {engagement.engagement_code}")

        return engagement

    async def set_status(
        self,
        engagement_id: int,
        new_status: EngagementStatus,
        notes: Optional[str] = None,
        actor: Optional[str] = None
    ) -> FacilitatorEngagement:
        """
        Change engagement status with validation.

        Args:
            engagement_id: Engagement ID
            new_status: Target status
            notes: Optional notes about the change
            actor: User making the change

        Returns:
            Updated engagement

        Raises:
            ValueError: If transition is invalid or engagement not found
        """
        engagement = await self.get_engagement(engagement_id)
        if not engagement:
            raise ValueError(f"Engagement {engagement_id} not found")

        old_status = engagement.status

        # Validate transition
        self.workflow_service.validate_transition(old_status, new_status)

        # Update status
        update_data = {"status": new_status}
        if notes:
            update_data["notes"] = f"{engagement.notes or ''}\n[{datetime.now()}] {notes}".strip()

        engagement = await self.engagement_repo.update(engagement_id, **update_data)

        # Log event
        await self.event_repo.log_event(
            event_type=EventType.ENGAGEMENT_STATUS_CHANGED,
            engagement_id=engagement.id,
            description=f"Status changed: {old_status.value} → {new_status.value}",
            actor=actor,
            payload={
                "old_status": old_status.value,
                "new_status": new_status.value,
                "notes": notes
            }
        )

        await self.db.commit()

        logger.info(
            f"Changed engagement {engagement.engagement_code} status: "
            f"{old_status.value} → {new_status.value}"
        )

        return engagement

    async def terminate_engagement(
        self,
        engagement_id: int,
        reason: str,
        actor: Optional[str] = None
    ) -> FacilitatorEngagement:
        """
        Terminate an engagement.

        Args:
            engagement_id: Engagement ID
            reason: Reason for termination
            actor: User terminating the engagement

        Returns:
            Updated engagement
        """
        engagement = await self.set_status(
            engagement_id,
            EngagementStatus.TERMINATED,
            notes=f"Terminated: {reason}",
            actor=actor
        )

        # Set end date
        engagement = await self.engagement_repo.update(
            engagement_id,
            end_date=datetime.now()
        )

        await self.db.commit()

        return engagement
