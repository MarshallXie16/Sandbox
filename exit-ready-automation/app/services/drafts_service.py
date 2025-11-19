"""
Service for generating document drafts (teaser, summary, CIM).
"""
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import CaseRepository, EventRepository
from app.core.workflow import CaseStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


class DraftsService:
    """Service for generating business document drafts."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.case_repo = CaseRepository(session)
        self.event_repo = EventRepository(session)

    async def generate_drafts(
        self,
        case_id: int,
        actor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate teaser, summary, and CIM drafts.

        Args:
            case_id: Case ID
            actor: Who triggered generation

        Returns:
            Dictionary with draft content

        Raises:
            ValueError: If case not found or valuation not done
        """
        case = await self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        if not case.valuation_payload:
            raise ValueError(
                f"Case {case.case_code} does not have valuation results. "
                "Run valuation first."
            )

        # Generate drafts (simplified templates for now)
        # In production, this would use GPT or template engine
        drafts = {
            "teaser": self._generate_teaser(case),
            "exit_summary": self._generate_exit_summary(case),
            "cim_sections": self._generate_cim_sections(case),
        }

        # Store drafts
        await self.case_repo.update(case_id, {
            "drafts": drafts,
            "drafts_generated_at": datetime.utcnow(),
            "status": CaseStatus.DRAFTS_GENERATED.value,
        })

        # Log event
        await self.event_repo.create({
            "case_id": case_id,
            "event_type": "drafts_generated",
            "payload": {
                "sections": list(drafts.keys()),
                "generated_at": datetime.utcnow().isoformat(),
            },
            "actor": actor or "system",
        })

        await self.session.commit()

        logger.info(f"Generated drafts for case {case.case_code}")

        return drafts

    def _generate_teaser(self, case) -> Dict[str, str]:
        """Generate one-page teaser."""
        valuation = case.valuation_payload or {}
        val_range = valuation.get("valuation_range", {})

        return {
            "title": f"Opportunity: {case.company_name}",
            "headline": f"{case.industry or 'Established'} Business for Sale",
            "overview": (
                f"Well-established {case.industry or 'business'} with strong fundamentals "
                f"and growth potential."
            ),
            "financials_summary": (
                f"Asking Price Range: ${val_range.get('low', 0):,.0f} - "
                f"${val_range.get('high', 0):,.0f}"
            ),
            "highlights": [
                "Established customer base",
                "Proven business model",
                "Growth opportunities",
            ],
        }

    def _generate_exit_summary(self, case) -> Dict[str, Any]:
        """Generate exit summary."""
        valuation = case.valuation_payload or {}
        val_range = valuation.get("valuation_range", {})

        return {
            "executive_summary": f"Exit Ready assessment for {case.company_name}",
            "business_overview": {
                "name": case.company_name,
                "industry": case.industry,
                "region": case.region,
            },
            "valuation_summary": {
                "range_low": val_range.get("low", 0),
                "range_mid": val_range.get("mid", 0),
                "range_high": val_range.get("high", 0),
                "methodology": valuation.get("methodology", "Multiple-based"),
            },
            "recommendations": [
                "Review financials with CPA",
                "Prepare transition plan",
                "Consider timing and market conditions",
            ],
        }

    def _generate_cim_sections(self, case) -> Dict[str, str]:
        """Generate CIM sections (simplified)."""
        return {
            "executive_summary": f"Confidential Information Memorandum for {case.company_name}",
            "business_description": f"{case.company_name} - {case.industry or 'Business'}",
            "products_services": "To be completed",
            "market_analysis": "To be completed",
            "financial_analysis": "Based on provided financials",
            "operations": "To be completed",
            "growth_opportunities": "To be completed",
        }

    async def update_drafts(
        self,
        case_id: int,
        updated_drafts: Dict[str, Any],
        actor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update drafts after human review.

        Args:
            case_id: Case ID
            updated_drafts: Updated draft content
            actor: Who updated

        Returns:
            Updated drafts
        """
        case = await self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        # Merge with existing drafts
        current_drafts = case.drafts or {}
        current_drafts.update(updated_drafts)

        await self.case_repo.update(case_id, {
            "drafts": current_drafts,
            "status": CaseStatus.UNDER_REVIEW.value,
        })

        await self.event_repo.create({
            "case_id": case_id,
            "event_type": "drafts_updated",
            "payload": {
                "sections_updated": list(updated_drafts.keys()),
            },
            "actor": actor or "system",
        })

        await self.session.commit()

        logger.info(f"Updated drafts for case {case.case_code}")

        return current_drafts
