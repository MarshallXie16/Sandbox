"""Read-only repository for Facilitator data."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.logging import get_logger
from app.repositories.base import BaseReadRepository

logger = get_logger(__name__)


class FacilitatorReadRepository(BaseReadRepository):
    """
    Read-only repository for querying Facilitator data.

    Assumes upstream Facilitator database has tables:
    - facilitator_engagements (with status, timestamps, pricing info)
    - introduced_buyers (with statuses, linked to engagements)
    - offers (linked to engagements and introduced buyers)
    - closings (linked to engagements)
    """

    def __init__(self, engine: Optional[AsyncEngine] = None):
        """Initialize Facilitator read repository."""
        super().__init__(engine)

    async def get_engagement_summary(self) -> Dict[str, int]:
        """
        Get engagement counts by status.

        Returns:
            Dictionary with total and by_status breakdown
        """
        if not self.is_available():
            logger.warning("Facilitator database not available")
            return {"total": 0, "by_status": {}}

        async with await self.get_session() as session:
            try:
                # Total engagements
                result = await session.execute(
                    text("SELECT COUNT(*) as count FROM facilitator_engagements")
                )
                total = result.scalar() or 0

                # By status
                result = await session.execute(
                    text(
                        "SELECT status, COUNT(*) as count FROM facilitator_engagements "
                        "GROUP BY status"
                    )
                )
                by_status = {row[0]: row[1] for row in result.fetchall()}

                return {
                    "total": total,
                    "by_status": by_status,
                }
            except Exception as e:
                logger.error(f"Error getting Facilitator engagement summary: {e}")
                return {"total": 0, "by_status": {}}

    async def get_revenue_summary(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Dict[str, float]:
        """
        Get revenue summary for closed engagements.

        Args:
            from_date: Start date filter (optional)
            to_date: End date filter (optional)

        Returns:
            Dictionary with revenue metrics
        """
        if not self.is_available():
            return {
                "total_offer_fees": 0.0,
                "total_success_fee_gross": 0.0,
                "total_success_fee_net": 0.0,
                "total_revenue": 0.0,
                "closed_success_count": 0,
            }

        async with await self.get_session() as session:
            try:
                # Build query with optional date filters
                query_str = """
                    SELECT
                        COUNT(*) as closed_count,
                        COALESCE(SUM(offer_fee_collected), 0) as total_offer_fees,
                        COALESCE(SUM(success_fee_gross_amount), 0) as total_success_gross,
                        COALESCE(SUM(success_fee_net_amount), 0) as total_success_net
                    FROM facilitator_engagements
                    WHERE status = 'closed_success'
                """

                if from_date:
                    query_str += f" AND created_at >= '{from_date.isoformat()}'"
                if to_date:
                    query_str += f" AND created_at <= '{to_date.isoformat()}'"

                result = await session.execute(text(query_str))
                row = result.fetchone()

                if not row:
                    return {
                        "total_offer_fees": 0.0,
                        "total_success_fee_gross": 0.0,
                        "total_success_fee_net": 0.0,
                        "total_revenue": 0.0,
                        "closed_success_count": 0,
                    }

                total_offer_fees = float(row[1] or 0)
                total_success_gross = float(row[2] or 0)
                total_success_net = float(row[3] or 0)

                return {
                    "total_offer_fees": total_offer_fees,
                    "total_success_fee_gross": total_success_gross,
                    "total_success_fee_net": total_success_net,
                    "total_revenue": total_offer_fees + total_success_net,
                    "closed_success_count": int(row[0] or 0),
                }
            except Exception as e:
                logger.error(f"Error getting Facilitator revenue summary: {e}")
                return {
                    "total_offer_fees": 0.0,
                    "total_success_fee_gross": 0.0,
                    "total_success_fee_net": 0.0,
                    "total_revenue": 0.0,
                    "closed_success_count": 0,
                }

    async def get_buyer_intro_funnel(
        self, engagement_id: Optional[UUID] = None
    ) -> Dict[str, int]:
        """
        Get buyer introduction funnel metrics.

        Args:
            engagement_id: Filter by specific engagement (optional)

        Returns:
            Dictionary with counts for each funnel stage
        """
        if not self.is_available():
            return {
                "introduced": 0,
                "nda_signed": 0,
                "teaser_sent": 0,
                "info_access": 0,
                "offer": 0,
                "closing": 0,
            }

        async with await self.get_session() as session:
            try:
                # Build base query
                where_clause = ""
                if engagement_id:
                    where_clause = f" WHERE engagement_id = '{engagement_id}'"

                query_str = f"""
                    SELECT
                        COUNT(*) as total_introduced,
                        COUNT(CASE WHEN nda_signed_at IS NOT NULL THEN 1 END) as nda_signed,
                        COUNT(CASE WHEN teaser_sent_at IS NOT NULL THEN 1 END) as teaser_sent,
                        COUNT(CASE WHEN info_room_access_at IS NOT NULL THEN 1 END) as info_access,
                        COUNT(CASE WHEN offer_submitted_at IS NOT NULL THEN 1 END) as offer,
                        COUNT(CASE WHEN closing_completed_at IS NOT NULL THEN 1 END) as closing
                    FROM introduced_buyers
                    {where_clause}
                """

                result = await session.execute(text(query_str))
                row = result.fetchone()

                if not row:
                    return {
                        "introduced": 0,
                        "nda_signed": 0,
                        "teaser_sent": 0,
                        "info_access": 0,
                        "offer": 0,
                        "closing": 0,
                    }

                return {
                    "introduced": int(row[0] or 0),
                    "nda_signed": int(row[1] or 0),
                    "teaser_sent": int(row[2] or 0),
                    "info_access": int(row[3] or 0),
                    "offer": int(row[4] or 0),
                    "closing": int(row[5] or 0),
                }
            except Exception as e:
                logger.error(f"Error getting buyer intro funnel: {e}")
                return {
                    "introduced": 0,
                    "nda_signed": 0,
                    "teaser_sent": 0,
                    "info_access": 0,
                    "offer": 0,
                    "closing": 0,
                }

    async def get_offer_counts(self, engagement_id: Optional[UUID] = None) -> Dict[str, int]:
        """
        Get offer counts and statistics.

        Args:
            engagement_id: Filter by specific engagement (optional)

        Returns:
            Dictionary with offer metrics
        """
        if not self.is_available():
            return {"total_offers": 0, "by_status": {}}

        async with await self.get_session() as session:
            try:
                where_clause = ""
                if engagement_id:
                    where_clause = f" WHERE engagement_id = '{engagement_id}'"

                # Total offers
                result = await session.execute(
                    text(f"SELECT COUNT(*) as count FROM offers{where_clause}")
                )
                total = result.scalar() or 0

                # By status
                result = await session.execute(
                    text(
                        f"SELECT status, COUNT(*) as count FROM offers{where_clause} "
                        "GROUP BY status"
                    )
                )
                by_status = {row[0]: row[1] for row in result.fetchall()}

                return {
                    "total_offers": total,
                    "by_status": by_status,
                }
            except Exception as e:
                logger.error(f"Error getting offer counts: {e}")
                return {"total_offers": 0, "by_status": {}}
