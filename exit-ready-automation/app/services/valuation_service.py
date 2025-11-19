"""
Service for running valuations.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import CaseRepository, EventRepository
from app.integrations import ValuationEngineClient
from app.schemas.valuation import ValuationResponse
from app.core.workflow import CaseStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


class ValuationService:
    """Service for running business valuations."""

    def __init__(
        self,
        session: AsyncSession,
        valuation_client: Optional[ValuationEngineClient] = None
    ):
        self.session = session
        self.case_repo = CaseRepository(session)
        self.event_repo = EventRepository(session)
        self.valuation_client = valuation_client or ValuationEngineClient()

    async def run_valuation(
        self,
        case_id: int,
        actor: Optional[str] = None
    ) -> ValuationResponse:
        """
        Run valuation for a case.

        Args:
            case_id: Case ID
            actor: Who triggered the valuation

        Returns:
            Valuation response

        Raises:
            ValueError: If case not found or financials not ready
        """
        case = await self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        if not case.normalized_financials:
            raise ValueError(
                f"Case {case.case_code} does not have normalized financials. "
                "Run financial normalization first."
            )

        # Prepare metadata
        metadata = {
            "business_name": case.company_name,
            "industry": case.industry or "Unknown",
            "region": case.region,
            "case_code": case.case_code,
        }

        # Call valuation engine
        valuation_result = await self.valuation_client.run_valuation(
            normalized_financials=case.normalized_financials,
            metadata=metadata
        )

        # Store result
        await self.case_repo.update(case_id, {
            "valuation_payload": valuation_result.model_dump(),
            "valuation_last_run_at": datetime.utcnow(),
            "status": CaseStatus.VALUATION_DONE.value,
        })

        # Log event
        await self.event_repo.create({
            "case_id": case_id,
            "event_type": "valuation_run",
            "payload": {
                "valuation_range": valuation_result.valuation_range.model_dump(),
                "methodology": valuation_result.methodology,
                "confidence": valuation_result.confidence_level,
            },
            "actor": actor or "system",
        })

        await self.session.commit()

        logger.info(
            f"Valuation completed for case {case.case_code}: "
            f"${valuation_result.valuation_range.low:,.0f} - "
            f"${valuation_result.valuation_range.high:,.0f}"
        )

        return valuation_result
