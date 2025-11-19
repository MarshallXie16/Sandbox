"""
Service for delivering Exit Ready reports.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import CaseRepository, EventRepository
from app.integrations import EmailEngineClient
from app.core.workflow import CaseStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


class ExportService:
    """Service for exporting reports to PDF."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.case_repo = CaseRepository(session)
        self.event_repo = EventRepository(session)

    async def export_exit_ready_report(
        self,
        case_id: int,
        actor: Optional[str] = None
    ) -> str:
        """
        Export Exit Ready report to PDF.

        Args:
            case_id: Case ID
            actor: Who triggered export

        Returns:
            URL to generated PDF

        Raises:
            ValueError: If case or drafts not found
        """
        case = await self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        if not case.drafts:
            raise ValueError(
                f"Case {case.case_code} does not have drafts. "
                "Generate drafts first."
            )

        # TODO: Implement actual PDF generation
        # For now, generate a stub URL
        report_url = f"https://storage.example.com/reports/{case.case_code}_exit_ready.pdf"

        await self.case_repo.update(case_id, {
            "report_url": report_url,
            "report_ready_at": datetime.utcnow(),
            "status": CaseStatus.REPORT_READY.value,
        })

        await self.event_repo.create({
            "case_id": case_id,
            "event_type": "report_exported",
            "payload": {
                "report_url": report_url,
                "format": "pdf",
            },
            "actor": actor or "system",
        })

        await self.session.commit()

        logger.info(f"Exported Exit Ready report for case {case.case_code}")

        return report_url


class DeliveryService:
    """Service for delivering reports to sellers."""

    def __init__(
        self,
        session: AsyncSession,
        email_client: Optional[EmailEngineClient] = None
    ):
        self.session = session
        self.case_repo = CaseRepository(session)
        self.event_repo = EventRepository(session)
        self.email_client = email_client or EmailEngineClient()

    async def deliver_report(
        self,
        case_id: int,
        channel: str = "email",
        actor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deliver Exit Ready report to seller.

        Args:
            case_id: Case ID
            channel: Delivery channel (email, in_person, etc.)
            actor: Who triggered delivery

        Returns:
            Delivery result

        Raises:
            ValueError: If case or report not found
        """
        case = await self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        if not case.report_url:
            raise ValueError(
                f"Case {case.case_code} does not have a report. "
                "Export report first."
            )

        result = {}

        if channel == "email":
            # Send via email
            result = await self.email_client.send_report_delivery(
                to=case.owner_email,
                owner_name=case.owner_name,
                company_name=case.company_name,
                report_url=case.report_url,
                case_code=case.case_code,
            )

        # Update case
        await self.case_repo.update(case_id, {
            "delivered_at": datetime.utcnow(),
            "delivery_channel": channel,
            "status": CaseStatus.DELIVERED.value,
        })

        # Log event
        await self.event_repo.create({
            "case_id": case_id,
            "event_type": "report_delivered",
            "payload": {
                "channel": channel,
                "to": case.owner_email if channel == "email" else None,
                "result": result,
            },
            "actor": actor or "system",
        })

        await self.session.commit()

        logger.info(
            f"Delivered Exit Ready report for case {case.case_code} via {channel}"
        )

        return result

    async def close_case(
        self,
        case_id: int,
        next_step: str = "none",
        notes: Optional[str] = None,
        actor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Close an Exit Ready case.

        Args:
            case_id: Case ID
            next_step: What happens next (none, hold, optimize, facilitator, etc.)
            notes: Closing notes
            actor: Who closed the case

        Returns:
            Case closure confirmation
        """
        case = await self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        await self.case_repo.update(case_id, {
            "status": CaseStatus.CLOSED.value,
            "next_step": next_step,
            "notes": notes or case.notes,
        })

        await self.event_repo.create({
            "case_id": case_id,
            "event_type": "case_closed",
            "payload": {
                "next_step": next_step,
                "notes": notes,
            },
            "actor": actor or "system",
        })

        await self.session.commit()

        logger.info(f"Closed case {case.case_code} with next_step={next_step}")

        return {
            "case_code": case.case_code,
            "status": "closed",
            "next_step": next_step,
        }
