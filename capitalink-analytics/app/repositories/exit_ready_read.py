"""Read-only repository for Exit Ready data."""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.logging import get_logger
from app.repositories.base import BaseReadRepository

logger = get_logger(__name__)


class ExitReadyReadRepository(BaseReadRepository):
    """
    Read-only repository for querying Exit Ready data.

    Assumes upstream Exit Ready database has table:
    - exit_ready_cases (with status, timestamps, seller_contact_id, company_id)
    """

    def __init__(self, engine: Optional[AsyncEngine] = None):
        """Initialize Exit Ready read repository."""
        super().__init__(engine)

    async def get_pipeline_summary(self) -> Dict[str, int]:
        """
        Get case counts by status.

        Returns:
            Dictionary with total and by_status breakdown
        """
        if not self.is_available():
            logger.warning("Exit Ready database not available")
            return {"total": 0, "by_status": {}}

        async with await self.get_session() as session:
            try:
                # Total cases
                result = await session.execute(
                    text("SELECT COUNT(*) as count FROM exit_ready_cases")
                )
                total = result.scalar() or 0

                # By status
                result = await session.execute(
                    text(
                        "SELECT status, COUNT(*) as count FROM exit_ready_cases "
                        "GROUP BY status"
                    )
                )
                by_status = {row[0]: row[1] for row in result.fetchall()}

                return {
                    "total": total,
                    "by_status": by_status,
                }
            except Exception as e:
                logger.error(f"Error getting Exit Ready pipeline summary: {e}")
                return {"total": 0, "by_status": {}}

    async def get_cases_with_timestamps(
        self,
    ) -> List[Dict]:
        """
        Get all cases with their key timestamps for duration analysis.

        Returns:
            List of case dictionaries with timestamps
        """
        if not self.is_available():
            return []

        async with await self.get_session() as session:
            try:
                query = text(
                    """
                    SELECT
                        id,
                        status,
                        created_at,
                        intake_completed_at,
                        docs_collecting_started_at,
                        financials_ready_at,
                        valuation_completed_at,
                        report_ready_at,
                        delivered_at,
                        closed_at
                    FROM exit_ready_cases
                    ORDER BY created_at DESC
                    """
                )
                result = await session.execute(query)
                rows = result.fetchall()

                cases = []
                for row in rows:
                    cases.append(
                        {
                            "id": row[0],
                            "status": row[1],
                            "created_at": row[2],
                            "intake_completed_at": row[3],
                            "docs_collecting_started_at": row[4],
                            "financials_ready_at": row[5],
                            "valuation_completed_at": row[6],
                            "report_ready_at": row[7],
                            "delivered_at": row[8],
                            "closed_at": row[9],
                        }
                    )

                return cases
            except Exception as e:
                logger.error(f"Error getting Exit Ready cases with timestamps: {e}")
                return []

    async def get_case_volume_by_month(
        self, from_date: Optional[datetime] = None, to_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get case volume grouped by month.

        Args:
            from_date: Start date (optional)
            to_date: End date (optional)

        Returns:
            List of dictionaries with month, created_count, delivered_count, closed_count
        """
        if not self.is_available():
            return []

        async with await self.get_session() as session:
            try:
                # Build query with optional date filters
                query_str = """
                    SELECT
                        TO_CHAR(created_at, 'YYYY-MM') as month,
                        COUNT(*) as created_count,
                        COUNT(delivered_at) as delivered_count,
                        COUNT(closed_at) as closed_count
                    FROM exit_ready_cases
                """

                if from_date or to_date:
                    conditions = []
                    if from_date:
                        conditions.append(f"created_at >= '{from_date.isoformat()}'")
                    if to_date:
                        conditions.append(f"created_at <= '{to_date.isoformat()}'")
                    query_str += " WHERE " + " AND ".join(conditions)

                query_str += " GROUP BY TO_CHAR(created_at, 'YYYY-MM') ORDER BY month"

                result = await session.execute(text(query_str))
                rows = result.fetchall()

                return [
                    {
                        "month": row[0],
                        "created": row[1],
                        "delivered": row[2],
                        "closed": row[3],
                    }
                    for row in rows
                ]
            except Exception as e:
                logger.error(f"Error getting Exit Ready volume by month: {e}")
                return []

    async def count_cases_linked_to_facilitator(self) -> int:
        """
        Count cases that led to a Facilitator engagement.

        Returns:
            Number of cases with a linked Facilitator engagement
        """
        if not self.is_available():
            return 0

        async with await self.get_session() as session:
            try:
                # This assumes there's a foreign key or link field
                # Adjust based on actual schema
                result = await session.execute(
                    text(
                        """
                        SELECT COUNT(DISTINCT erc.id)
                        FROM exit_ready_cases erc
                        WHERE EXISTS (
                            SELECT 1 FROM facilitator_engagements fe
                            WHERE fe.exit_ready_case_id = erc.id
                        )
                        """
                    )
                )
                return result.scalar() or 0
            except Exception as e:
                # If the query fails (e.g., table doesn't exist), return 0
                logger.warning(
                    f"Could not count Exit Ready to Facilitator conversions: {e}"
                )
                return 0
