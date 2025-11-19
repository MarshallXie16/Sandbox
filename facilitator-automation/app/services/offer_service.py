"""
Offer Service for Facilitator Automation.

Handles business logic for managing offers from introduced buyers.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models import FacilitatorOffer, OfferStatus, EventType
from app.repositories import OfferRepository, BuyerIntroRepository, EngagementRepository, EventRepository
from app.schemas import OfferCreate
from app.core.logging import get_logger

logger = get_logger(__name__)


class OfferService:
    """Service for offer operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.offer_repo = OfferRepository(db)
        self.buyer_intro_repo = BuyerIntroRepository(db)
        self.engagement_repo = EngagementRepository(db)
        self.event_repo = EventRepository(db)

    async def create_offer(
        self,
        engagement_id: int,
        data: OfferCreate,
        actor: Optional[str] = None
    ) -> FacilitatorOffer:
        """
        Record an offer from an introduced buyer.

        Args:
            engagement_id: Engagement ID
            data: Offer data
            actor: User recording the offer

        Returns:
            Created offer

        Raises:
            ValueError: If validation fails
        """
        # Verify engagement exists
        engagement = await self.engagement_repo.get_by_id(engagement_id)
        if not engagement:
            raise ValueError(f"Engagement {engagement_id} not found")

        # Verify buyer intro exists and belongs to this engagement
        buyer_intro = await self.buyer_intro_repo.get_by_id(data.buyer_intro_id)
        if not buyer_intro:
            raise ValueError(f"Buyer intro {data.buyer_intro_id} not found")
        if buyer_intro.engagement_id != engagement_id:
            raise ValueError(
                f"Buyer intro {data.buyer_intro_id} does not belong to "
                f"engagement {engagement_id}"
            )

        # Determine offer fee amount
        offer_fee_amount = data.offer_fee_amount or engagement.offer_fee_fixed

        # Create offer
        offer = await self.offer_repo.create(
            engagement_id=engagement_id,
            buyer_intro_id=data.buyer_intro_id,
            offer_date=data.offer_date,
            headline_price=data.headline_price,
            currency=data.currency,
            structure=data.structure,
            status=OfferStatus.RECEIVED,
            notes=data.notes,
            offer_fee_amount=offer_fee_amount,
            offer_fee_invoiced=False,
            offer_fee_paid=False
        )

        # Log event
        await self.event_repo.log_event(
            event_type=EventType.OFFER_RECEIVED,
            engagement_id=engagement_id,
            buyer_intro_id=buyer_intro.id,
            offer_id=offer.id,
            description=f"Offer received: {data.currency} {data.headline_price:,.2f}",
            actor=actor,
            payload={
                "buyer_contact_id": buyer_intro.buyer_contact_id,
                "headline_price": float(data.headline_price),
                "currency": data.currency,
                "offer_fee_amount": float(offer_fee_amount)
            }
        )

        await self.db.commit()

        logger.info(
            f"Created offer {offer.id} for engagement {engagement.engagement_code}: "
            f"{data.currency} {data.headline_price:,.2f}"
        )

        return offer

    async def set_status(
        self,
        offer_id: int,
        new_status: OfferStatus,
        notes: Optional[str] = None,
        actor: Optional[str] = None
    ) -> FacilitatorOffer:
        """Update offer status."""
        offer = await self.offer_repo.get_by_id(offer_id)
        if not offer:
            raise ValueError(f"Offer {offer_id} not found")

        old_status = offer.status
        update_data = {"status": new_status}

        if notes:
            current_notes = offer.notes or ""
            from datetime import datetime
            update_data["notes"] = f"{current_notes}\n[{datetime.now()}] {notes}".strip()

        offer = await self.offer_repo.update(offer_id, **update_data)

        # Log event
        await self.event_repo.log_event(
            event_type=EventType.OFFER_STATUS_CHANGED,
            engagement_id=offer.engagement_id,
            offer_id=offer.id,
            description=f"Offer status changed: {old_status.value} → {new_status.value}",
            actor=actor,
            payload={
                "old_status": old_status.value,
                "new_status": new_status.value
            }
        )

        await self.db.commit()

        logger.info(f"Updated offer {offer_id} status: {old_status.value} → {new_status.value}")

        return offer

    async def mark_offer_fee(
        self,
        offer_id: int,
        invoiced: Optional[bool] = None,
        paid: Optional[bool] = None,
        actor: Optional[str] = None
    ) -> FacilitatorOffer:
        """Mark offer fee as invoiced/paid."""
        offer = await self.offer_repo.get_by_id(offer_id)
        if not offer:
            raise ValueError(f"Offer {offer_id} not found")

        await self.offer_repo.mark_fee_status(offer_id, invoiced, paid)

        # Log event
        if invoiced:
            await self.event_repo.log_event(
                event_type=EventType.OFFER_FEE_INVOICED,
                engagement_id=offer.engagement_id,
                offer_id=offer.id,
                description=f"Offer fee invoiced: {offer.currency} {offer.offer_fee_amount:,.2f}",
                actor=actor
            )
        if paid:
            await self.event_repo.log_event(
                event_type=EventType.OFFER_FEE_PAID,
                engagement_id=offer.engagement_id,
                offer_id=offer.id,
                description=f"Offer fee paid: {offer.currency} {offer.offer_fee_amount:,.2f}",
                actor=actor
            )

        await self.db.commit()

        return await self.offer_repo.get_by_id(offer_id)

    async def list_by_engagement(
        self,
        engagement_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[FacilitatorOffer]:
        """List all offers for an engagement."""
        return await self.offer_repo.get_by_engagement(engagement_id, skip, limit)
