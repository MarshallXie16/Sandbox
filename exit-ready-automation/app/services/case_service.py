"""
Service for Exit Ready case management.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import CaseRepository, EventRepository
from app.core.workflow import WorkflowService, CaseStatus, InvalidTransitionError
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse
from app.core.logging import get_logger

logger = get_logger(__name__)


class CaseService:
    """Service for managing Exit Ready cases."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.case_repo = CaseRepository(session)
        self.event_repo = EventRepository(session)

    async def create_case(
        self,
        case_data: CaseCreate,
        actor: Optional[str] = None
    ) -> CaseResponse:
        """
        Create a new Exit Ready case.

        Args:
            case_data: Case creation data
            actor: Who is creating the case

        Returns:
            Created case
        """
        # Generate case code
        case_code = await self.case_repo.generate_case_code()

        # Prepare case data
        create_data = {
            "case_code": case_code,
            "status": CaseStatus.CREATED.value,
            "owner_name": case_data.owner_name,
            "owner_email": case_data.owner_email,
            "company_name": case_data.company_name,
            "industry": case_data.industry,
            "region": case_data.region,
            "notes": case_data.notes,
            "contact_id": case_data.contact_id,
            "company_id": case_data.company_id,
        }

        # Create case
        case = await self.case_repo.create(create_data)

        # Log event
        await self.event_repo.create({
            "case_id": case.id,
            "event_type": "case_created",
            "payload": {
                "case_code": case_code,
                "owner_name": case_data.owner_name,
                "company_name": case_data.company_name,
            },
            "actor": actor or "system",
        })

        await self.session.commit()

        logger.info(f"Created case {case_code} for {case_data.company_name}")

        return CaseResponse.model_validate(case)

    async def get_case(
        self,
        case_id: int,
        include_documents: bool = False,
        include_events: bool = False
    ) -> Optional[CaseResponse]:
        """
        Get a case by ID.

        Args:
            case_id: Case ID
            include_documents: Load documents
            include_events: Load events

        Returns:
            Case or None
        """
        case = await self.case_repo.get_by_id(
            case_id,
            include_documents=include_documents,
            include_events=include_events
        )

        if not case:
            return None

        return CaseResponse.model_validate(case)

    async def get_case_by_code(self, case_code: str) -> Optional[CaseResponse]:
        """Get a case by case code."""
        case = await self.case_repo.get_by_case_code(case_code)
        if not case:
            return None
        return CaseResponse.model_validate(case)

    async def update_case(
        self,
        case_id: int,
        update_data: CaseUpdate,
        actor: Optional[str] = None
    ) -> Optional[CaseResponse]:
        """
        Update a case.

        Args:
            case_id: Case ID
            update_data: Update data
            actor: Who is updating

        Returns:
            Updated case or None
        """
        # Filter out None values
        update_dict = {
            k: v for k, v in update_data.model_dump().items()
            if v is not None
        }

        if not update_dict:
            # No updates
            return await self.get_case(case_id)

        case = await self.case_repo.update(case_id, update_dict)

        if not case:
            return None

        # Log event
        await self.event_repo.create({
            "case_id": case_id,
            "event_type": "case_updated",
            "payload": {"updates": update_dict},
            "actor": actor or "system",
        })

        await self.session.commit()

        logger.info(f"Updated case {case.case_code}")

        return CaseResponse.model_validate(case)

    async def update_status(
        self,
        case_id: int,
        new_status: CaseStatus,
        admin_override: bool = False,
        actor: Optional[str] = None
    ) -> CaseResponse:
        """
        Update case status with workflow validation.

        Args:
            case_id: Case ID
            new_status: New status
            admin_override: Allow any transition
            actor: Who triggered the change

        Returns:
            Updated case

        Raises:
            InvalidTransitionError: If transition not allowed
            ValueError: If case not found
        """
        case = await self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        current_status = CaseStatus(case.status)

        # Validate transition
        WorkflowService.validate_transition(
            current_status,
            new_status,
            admin_override=admin_override
        )

        # Update status
        case = await self.case_repo.update_status(case_id, new_status.value)

        # Log status change event
        await self.event_repo.log_status_change(
            case_id=case_id,
            from_status=current_status.value,
            to_status=new_status.value,
            actor=actor
        )

        await self.session.commit()

        logger.info(
            f"Case {case.case_code} status changed: "
            f"{current_status.value} → {new_status.value}"
        )

        return CaseResponse.model_validate(case)

    async def list_cases(
        self,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> tuple[List[CaseResponse], int]:
        """
        List cases with pagination.

        Args:
            status: Filter by status
            page: Page number
            page_size: Items per page

        Returns:
            Tuple of (cases, total_count)
        """
        cases, total = await self.case_repo.list_cases(
            status=status,
            page=page,
            page_size=page_size
        )

        case_responses = [CaseResponse.model_validate(c) for c in cases]

        return case_responses, total

    async def delete_case(
        self,
        case_id: int,
        actor: Optional[str] = None
    ) -> bool:
        """
        Delete a case.

        Args:
            case_id: Case ID
            actor: Who is deleting

        Returns:
            True if deleted
        """
        case = await self.case_repo.get_by_id(case_id)
        if not case:
            return False

        case_code = case.case_code

        # Log before deletion
        await self.event_repo.create({
            "case_id": case_id,
            "event_type": "case_deleted",
            "payload": {"case_code": case_code},
            "actor": actor or "system",
        })

        await self.session.commit()

        deleted = await self.case_repo.delete(case_id)

        if deleted:
            await self.session.commit()
            logger.info(f"Deleted case {case_code}")

        return deleted

    async def get_stats(self) -> Dict[str, Any]:
        """Get case statistics."""
        return await self.case_repo.get_stats()
