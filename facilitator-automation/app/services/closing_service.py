"""
Closing Service for Facilitator Automation.

Handles business logic for recording deal closings and calculating success fees.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models import FacilitatorClosing, EventType, EngagementStatus
from app.repositories import (
    ClosingRepository,
    BuyerIntroRepository,
    EngagementRepository,
    OfferRepository,
    EventRepository
)
from app.schemas import ClosingCreate
from app.services.fee_calculator import FeeCalculatorService
from app.core.logging import get_logger

logger = get_logger(__name__)


class ClosingService:
    """Service for closing operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.closing_repo = ClosingRepository(db)
        self.buyer_intro_repo = BuyerIntroRepository(db)
        self.engagement_repo = EngagementRepository(db)
        self.offer_repo = OfferRepository(db)
        self.event_repo = EventRepository(db)
        self.fee_calculator = FeeCalculatorService()

    async def record_closing(
        self,
        engagement_id: int,
        data: ClosingCreate,
        actor: Optional[str] = None
    ) -> FacilitatorClosing:
        """
        Record a deal closing with an introduced buyer.

        This is the critical operation for success fee calculation. The buyer
        MUST be an Introduced Buyer (have an entry in facilitator_buyer_intros).

        Args:
            engagement_id: Engagement ID
            data: Closing data
            actor: User recording the closing

        Returns:
            Created closing with calculated fees

        Raises:
            ValueError: If validation fails or buyer not introduced
        """
        # Verify engagement exists
        engagement = await self.engagement_repo.get_by_id(engagement_id)
        if not engagement:
            raise ValueError(f"Engagement {engagement_id} not found")

        # Check if closing already exists
        existing_closing = await self.closing_repo.get_by_engagement(engagement_id)
        if existing_closing:
            raise ValueError(
                f"Closing already exists for engagement {engagement.engagement_code} "
                f"(closing_id={existing_closing.id})"
            )

        # CRITICAL: Verify buyer is an Introduced Buyer
        buyer_intro = await self.buyer_intro_repo.get_by_id(data.buyer_intro_id)
        if not buyer_intro:
            raise ValueError(
                f"Buyer intro {data.buyer_intro_id} not found. "
                "Cannot record closing: buyer must be an Introduced Buyer."
            )
        if buyer_intro.engagement_id != engagement_id:
            raise ValueError(
                f"Buyer intro {data.buyer_intro_id} does not belong to "
                f"engagement {engagement_id}"
            )

        # Get paid offer fees for this buyer (for credit calculation)
        offer_fees_paid = await self.offer_repo.get_paid_offer_fees_for_buyer(
            buyer_intro.id
        )

        # Calculate success fee using FeeCalculatorService
        fee_calculation = self.fee_calculator.calculate_success_fee(
            final_price=data.final_price,
            success_fee_rate=engagement.success_fee_rate,
            offer_fees_paid=offer_fees_paid
        )

        # Create closing record
        closing = await self.closing_repo.create(
            engagement_id=engagement_id,
            buyer_intro_id=buyer_intro.id,
            closing_date=data.closing_date,
            final_price=data.final_price,
            currency=data.currency,
            final_structure=data.final_structure,
            success_fee_rate=engagement.success_fee_rate,
            success_fee_gross_amount=fee_calculation.success_fee_gross,
            offer_fee_credit_amount=fee_calculation.offer_fee_credit,
            success_fee_net_amount=fee_calculation.success_fee_net,
            invoiced=False,
            paid=False,
            notes=data.notes
        )

        # Update engagement status to CLOSED_SUCCESS
        await self.engagement_repo.update(
            engagement_id,
            status=EngagementStatus.CLOSED_SUCCESS
        )

        # Log event
        await self.event_repo.log_event(
            event_type=EventType.CLOSING_RECORDED,
            engagement_id=engagement_id,
            buyer_intro_id=buyer_intro.id,
            closing_id=closing.id,
            description=(
                f"Closing recorded: {data.currency} {data.final_price:,.2f} "
                f"(success fee net: {data.currency} {fee_calculation.success_fee_net:,.2f})"
            ),
            actor=actor,
            payload={
                "buyer_contact_id": buyer_intro.buyer_contact_id,
                "final_price": float(data.final_price),
                "currency": data.currency,
                "success_fee_gross": float(fee_calculation.success_fee_gross),
                "offer_fee_credit": float(fee_calculation.offer_fee_credit),
                "success_fee_net": float(fee_calculation.success_fee_net),
                "total_revenue": float(fee_calculation.total_facilitator_revenue)
            }
        )

        await self.db.commit()

        logger.info(
            f"Recorded closing for engagement {engagement.engagement_code}: "
            f"{data.currency} {data.final_price:,.2f}. "
            f"Success fee net: {data.currency} {fee_calculation.success_fee_net:,.2f} "
            f"(gross: {fee_calculation.success_fee_gross:,.2f}, "
            f"credit: {fee_calculation.offer_fee_credit:,.2f})"
        )

        return closing

    async def get_closing(
        self,
        closing_id: int
    ) -> Optional[FacilitatorClosing]:
        """Get closing by ID."""
        return await self.closing_repo.get_by_id(closing_id)

    async def get_by_engagement(
        self,
        engagement_id: int
    ) -> Optional[FacilitatorClosing]:
        """Get closing for an engagement."""
        return await self.closing_repo.get_by_engagement(engagement_id)

    async def mark_invoiced(
        self,
        closing_id: int,
        invoiced: Optional[bool] = None,
        paid: Optional[bool] = None,
        actor: Optional[str] = None
    ) -> FacilitatorClosing:
        """Mark closing as invoiced/paid."""
        closing = await self.closing_repo.get_by_id(closing_id)
        if not closing:
            raise ValueError(f"Closing {closing_id} not found")

        await self.closing_repo.mark_invoiced(closing_id, invoiced, paid)

        # Log events
        if invoiced:
            await self.event_repo.log_event(
                event_type=EventType.SUCCESS_FEE_INVOICED,
                engagement_id=closing.engagement_id,
                closing_id=closing.id,
                description=f"Success fee invoiced: {closing.currency} {closing.success_fee_net_amount:,.2f}",
                actor=actor
            )
        if paid:
            await self.event_repo.log_event(
                event_type=EventType.SUCCESS_FEE_PAID,
                engagement_id=closing.engagement_id,
                closing_id=closing.id,
                description=f"Success fee paid: {closing.currency} {closing.success_fee_net_amount:,.2f}",
                actor=actor
            )

        await self.db.commit()

        return await self.closing_repo.get_by_id(closing_id)
