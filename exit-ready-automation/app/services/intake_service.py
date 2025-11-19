"""
Service for managing intake forms.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import CaseRepository, EventRepository
from app.integrations import EmailEngineClient
from app.core.config import settings
from app.core.workflow import CaseStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


class IntakeService:
    """Service for intake form management."""

    def __init__(
        self,
        session: AsyncSession,
        email_client: Optional[EmailEngineClient] = None
    ):
        self.session = session
        self.case_repo = CaseRepository(session)
        self.event_repo = EventRepository(session)
        self.email_client = email_client or EmailEngineClient()

    async def generate_intake_url(
        self,
        case_id: int
    ) -> str:
        """
        Generate unique intake form URL for a case.

        Args:
            case_id: Case ID

        Returns:
            Intake form URL
        """
        case = await self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        # Generate unique token (in production, use proper token generation)
        token = f"{case.case_code}_{case.id}_{hash(case.owner_email)}"

        # Build URL
        intake_url = f"{settings.intake_form_base_url}/{token}"

        # Update case with intake URL
        await self.case_repo.update(case_id, {
            "intake_form_url": intake_url,
        })

        logger.info(f"Generated intake URL for case {case.case_code}: {intake_url}")

        return intake_url

    async def send_intake_link(
        self,
        case_id: int,
        actor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send intake form link to seller.

        Args:
            case_id: Case ID
            actor: Who triggered the send

        Returns:
            Send result
        """
        case = await self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        # Generate intake URL if not exists
        intake_url = case.intake_form_url
        if not intake_url:
            intake_url = await self.generate_intake_url(case_id)

        # Send email
        result = await self.email_client.send_intake_link(
            to=case.owner_email,
            owner_name=case.owner_name,
            company_name=case.company_name,
            intake_url=intake_url,
            case_code=case.case_code,
        )

        # Update case
        await self.case_repo.update(case_id, {
            "intake_sent_at": datetime.utcnow(),
            "status": CaseStatus.INTAKE_PENDING.value,
        })

        # Log event
        await self.event_repo.create({
            "case_id": case_id,
            "event_type": "intake_sent",
            "payload": {
                "to": case.owner_email,
                "intake_url": intake_url,
                "result": result,
            },
            "actor": actor or "system",
        })

        await self.session.commit()

        logger.info(f"Sent intake link for case {case.case_code} to {case.owner_email}")

        return result

    async def import_intake_data(
        self,
        case_id: int,
        intake_data: Dict[str, Any],
        actor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Import intake form responses.

        Args:
            case_id: Case ID
            intake_data: Intake form data
            actor: Who imported

        Returns:
            Updated case
        """
        case = await self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        # Update case with intake data
        update_data = {
            "intake_payload": intake_data,
            "intake_received_at": datetime.utcnow(),
            "status": CaseStatus.INTAKE_DONE.value,
        }

        # Extract and update any top-level fields if present in intake
        if "industry" in intake_data and not case.industry:
            update_data["industry"] = intake_data["industry"]

        if "region" in intake_data and not case.region:
            update_data["region"] = intake_data["region"]

        case = await self.case_repo.update(case_id, update_data)

        # Log event
        await self.event_repo.create({
            "case_id": case_id,
            "event_type": "intake_imported",
            "payload": {
                "data_keys": list(intake_data.keys()),
                "imported_at": datetime.utcnow().isoformat(),
            },
            "actor": actor or "system",
        })

        await self.session.commit()

        logger.info(f"Imported intake data for case {case.case_code}")

        return {"status": "imported", "case_code": case.case_code}
