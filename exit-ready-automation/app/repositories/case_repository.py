"""
Repository for Exit Ready case database operations.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import ExitReadyCase
from app.core.workflow import CaseStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


class CaseRepository:
    """Repository for Exit Ready case data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, case_data: Dict[str, Any]) -> ExitReadyCase:
        """
        Create a new Exit Ready case.

        Args:
            case_data: Dictionary of case attributes

        Returns:
            Created ExitReadyCase instance
        """
        case = ExitReadyCase(**case_data)
        self.session.add(case)
        await self.session.flush()
        await self.session.refresh(case)
        logger.info(f"Created case {case.case_code} (ID: {case.id})")
        return case

    async def get_by_id(
        self,
        case_id: int,
        include_documents: bool = False,
        include_events: bool = False
    ) -> Optional[ExitReadyCase]:
        """
        Get a case by ID.

        Args:
            case_id: Case ID
            include_documents: Whether to eagerly load documents
            include_events: Whether to eagerly load events

        Returns:
            ExitReadyCase or None if not found
        """
        query = select(ExitReadyCase).where(ExitReadyCase.id == case_id)

        if include_documents:
            query = query.options(selectinload(ExitReadyCase.documents))
        if include_events:
            query = query.options(selectinload(ExitReadyCase.events))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_case_code(self, case_code: str) -> Optional[ExitReadyCase]:
        """
        Get a case by case code.

        Args:
            case_code: Case code (e.g., ER-2025-0001)

        Returns:
            ExitReadyCase or None if not found
        """
        query = select(ExitReadyCase).where(ExitReadyCase.case_code == case_code)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_contact_id(self, contact_id: int) -> List[ExitReadyCase]:
        """
        Get all cases for a contact.

        Args:
            contact_id: Contact ID from CRM

        Returns:
            List of ExitReadyCase instances
        """
        query = select(ExitReadyCase).where(
            ExitReadyCase.contact_id == contact_id
        ).order_by(ExitReadyCase.created_at.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_cases(
        self,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[List[ExitReadyCase], int]:
        """
        List cases with pagination and filtering.

        Args:
            status: Filter by status
            page: Page number (1-indexed)
            page_size: Number of items per page
            order_by: Field to order by
            order_desc: Order descending if True

        Returns:
            Tuple of (list of cases, total count)
        """
        # Build filter
        filters = []
        if status:
            filters.append(ExitReadyCase.status == status)

        # Count query
        count_query = select(func.count(ExitReadyCase.id))
        if filters:
            count_query = count_query.where(and_(*filters))

        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        # Data query
        query = select(ExitReadyCase)
        if filters:
            query = query.where(and_(*filters))

        # Order by
        order_field = getattr(ExitReadyCase, order_by, ExitReadyCase.created_at)
        if order_desc:
            query = query.order_by(order_field.desc())
        else:
            query = query.order_by(order_field)

        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.session.execute(query)
        cases = list(result.scalars().all())

        return cases, total

    async def update(
        self,
        case_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[ExitReadyCase]:
        """
        Update a case.

        Args:
            case_id: Case ID
            update_data: Dictionary of fields to update

        Returns:
            Updated ExitReadyCase or None if not found
        """
        case = await self.get_by_id(case_id)
        if not case:
            return None

        for key, value in update_data.items():
            if hasattr(case, key):
                setattr(case, key, value)

        case.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(case)
        logger.info(f"Updated case {case.case_code} (ID: {case.id})")
        return case

    async def update_status(
        self,
        case_id: int,
        new_status: str
    ) -> Optional[ExitReadyCase]:
        """
        Update case status.

        Args:
            case_id: Case ID
            new_status: New status value

        Returns:
            Updated ExitReadyCase or None if not found
        """
        return await self.update(case_id, {"status": new_status})

    async def delete(self, case_id: int) -> bool:
        """
        Delete a case.

        Args:
            case_id: Case ID

        Returns:
            True if deleted, False if not found
        """
        case = await self.get_by_id(case_id)
        if not case:
            return False

        await self.session.delete(case)
        logger.info(f"Deleted case {case.case_code} (ID: {case.id})")
        return True

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get case statistics.

        Returns:
            Dictionary of statistics
        """
        # Total cases
        total_query = select(func.count(ExitReadyCase.id))
        total_result = await self.session.execute(total_query)
        total = total_result.scalar_one()

        # By status
        status_query = select(
            ExitReadyCase.status,
            func.count(ExitReadyCase.id)
        ).group_by(ExitReadyCase.status)
        status_result = await self.session.execute(status_query)
        by_status = {status: count for status, count in status_result.all()}

        return {
            "total_cases": total,
            "by_status": by_status,
        }

    async def generate_case_code(self, year: Optional[int] = None) -> str:
        """
        Generate a unique case code.

        Format: ER-YYYY-NNNN

        Args:
            year: Year to use (defaults to current year)

        Returns:
            Generated case code
        """
        if year is None:
            year = datetime.utcnow().year

        # Find the highest number for this year
        prefix = f"ER-{year}-"
        query = select(ExitReadyCase.case_code).where(
            ExitReadyCase.case_code.like(f"{prefix}%")
        ).order_by(ExitReadyCase.case_code.desc()).limit(1)

        result = await self.session.execute(query)
        last_code = result.scalar_one_or_none()

        if last_code:
            # Extract number and increment
            last_num = int(last_code.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}{new_num:04d}"
