"""
Buyer Intro Service for Facilitator Automation.

Handles business logic for managing introduced buyers.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models import FacilitatorBuyerIntro, BuyerIntroStatus, EventType
from app.repositories import BuyerIntroRepository, EngagementRepository, EventRepository
from app.schemas import BuyerIntroCreate
from app.core.logging import get_logger

logger = get_logger(__name__)


class BuyerIntroService:
    """Service for buyer introduction operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.buyer_intro_repo = BuyerIntroRepository(db)
        self.engagement_repo = EngagementRepository(db)
        self.event_repo = EventRepository(db)

    async def introduce_buyer(
        self,
        engagement_id: int,
        data: BuyerIntroCreate,
        actor: Optional[str] = None
    ) -> FacilitatorBuyerIntro:
        """
        Introduce a buyer to an engagement.

        This creates an "Introduced Buyer" record, which is the source of truth
        for success fee eligibility.

        Args:
            engagement_id: Engagement ID
            data: Buyer intro data
            actor: User performing the introduction

        Returns:
            Created buyer intro

        Raises:
            ValueError: If engagement not found or buyer already introduced
        """
        # Verify engagement exists and is active
        engagement = await self.engagement_repo.get_by_id(engagement_id)
        if not engagement:
            raise ValueError(f"Engagement {engagement_id} not found")

        if not engagement.is_active():
            raise ValueError(
                f"Cannot introduce buyer: engagement {engagement.engagement_code} "
                f"is not active (status: {engagement.status.value})"
            )

        # Check if buyer already introduced
        existing = await self.buyer_intro_repo.get_by_buyer_and_engagement(
            data.buyer_contact_id,
            engagement_id
        )
        if existing:
            raise ValueError(
                f"Buyer {data.buyer_contact_id} has already been introduced "
                f"to engagement {engagement.engagement_code}"
            )

        # Create buyer intro
        buyer_intro = await self.buyer_intro_repo.create(
            engagement_id=engagement_id,
            buyer_contact_id=data.buyer_contact_id,
            introduction_channel=data.introduction_channel,
            status=BuyerIntroStatus.INVITED,
            notes=data.notes
        )

        # Log event
        await self.event_repo.log_event(
            event_type=EventType.BUYER_INTRODUCED,
            engagement_id=engagement_id,
            buyer_intro_id=buyer_intro.id,
            description=f"Buyer {data.buyer_contact_id} introduced via {data.introduction_channel.value}",
            actor=actor,
            payload={
                "buyer_contact_id": data.buyer_contact_id,
                "channel": data.introduction_channel.value
            }
        )

        await self.db.commit()

        logger.info(
            f"Introduced buyer {data.buyer_contact_id} to engagement "
            f"{engagement.engagement_code} (buyer_intro_id={buyer_intro.id})"
        )

        return buyer_intro

    async def set_status(
        self,
        buyer_intro_id: int,
        new_status: BuyerIntroStatus,
        notes: Optional[str] = None,
        actor: Optional[str] = None
    ) -> FacilitatorBuyerIntro:
        """
        Update buyer intro status and timestamp relevant fields.

        Args:
            buyer_intro_id: Buyer intro ID
            new_status: New status
            notes: Optional notes
            actor: User making the change

        Returns:
            Updated buyer intro
        """
        buyer_intro = await self.buyer_intro_repo.get_by_id(buyer_intro_id)
        if not buyer_intro:
            raise ValueError(f"Buyer intro {buyer_intro_id} not found")

        old_status = buyer_intro.status
        update_data = {"status": new_status}

        # Update timestamps based on status
        now = datetime.now()
        if new_status == BuyerIntroStatus.NDA_PENDING and not buyer_intro.nda_sent_at:
            update_data["nda_sent_at"] = now
        elif new_status == BuyerIntroStatus.NDA_SIGNED and not buyer_intro.nda_signed_at:
            update_data["nda_signed_at"] = now
        elif new_status == BuyerIntroStatus.TEASER_SENT and not buyer_intro.teaser_sent_at:
            update_data["teaser_sent_at"] = now
        elif new_status == BuyerIntroStatus.INFO_ACCESS and not buyer_intro.info_access_granted_at:
            update_data["info_access_granted_at"] = now

        update_data["last_contact_at"] = now

        if notes:
            current_notes = buyer_intro.notes or ""
            update_data["notes"] = f"{current_notes}\n[{now}] {notes}".strip()

        buyer_intro = await self.buyer_intro_repo.update(buyer_intro_id, **update_data)

        # Log event
        await self.event_repo.log_event(
            event_type=EventType.BUYER_STATUS_CHANGED,
            engagement_id=buyer_intro.engagement_id,
            buyer_intro_id=buyer_intro.id,
            description=f"Buyer status changed: {old_status.value} → {new_status.value}",
            actor=actor,
            payload={
                "old_status": old_status.value,
                "new_status": new_status.value,
                "notes": notes
            }
        )

        await self.db.commit()

        logger.info(
            f"Updated buyer intro {buyer_intro_id} status: "
            f"{old_status.value} → {new_status.value}"
        )

        return buyer_intro

    async def list_by_engagement(
        self,
        engagement_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorBuyerIntro]:
        """List all buyer intros for an engagement."""
        return await self.buyer_intro_repo.get_by_engagement(
            engagement_id, skip, limit
        )
