"""
Client for external Valuation Engine API.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.valuation import (
    ValuationRequest,
    ValuationResponse,
    ValuationStubResponse,
    ValuationRange,
    ValuationMultiples,
)

logger = get_logger(__name__)


class ValuationEngineError(Exception):
    """Base exception for valuation engine errors."""
    pass


class ValuationEngineClient:
    """
    Client for calling the external Valuation Engine API.

    Supports stub mode for development/testing when the real API is unavailable.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None,
        stub_mode: Optional[bool] = None,
    ):
        self.base_url = base_url or settings.valuation_engine_base_url
        self.api_key = api_key or settings.valuation_engine_api_key
        self.timeout = timeout or settings.valuation_engine_timeout
        self.stub_mode = stub_mode if stub_mode is not None else settings.valuation_engine_stub_mode

        logger.info(
            f"ValuationEngineClient initialized "
            f"(stub_mode={self.stub_mode}, base_url={self.base_url})"
        )

    async def run_valuation(
        self,
        normalized_financials: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> ValuationResponse:
        """
        Run a valuation using the external engine.

        Args:
            normalized_financials: Structured financial data
            metadata: Business metadata (name, industry, region, etc.)

        Returns:
            ValuationResponse with ranges and multiples

        Raises:
            ValuationEngineError: If API call fails
        """
        if self.stub_mode:
            return await self._run_stub_valuation(normalized_financials, metadata)

        return await self._run_real_valuation(normalized_financials, metadata)

    async def _run_real_valuation(
        self,
        normalized_financials: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> ValuationResponse:
        """Call the real valuation API."""
        try:
            payload = {
                "business_name": metadata.get("business_name", "Unknown"),
                "industry": metadata.get("industry", "Unknown"),
                "region": metadata.get("region"),
                "financials": normalized_financials,
                "metadata": metadata,
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/valuations",
                    json=payload,
                    headers=headers,
                )

                response.raise_for_status()
                data = response.json()

                # Parse response into ValuationResponse
                return ValuationResponse(**data)

        except httpx.HTTPStatusError as e:
            logger.error(f"Valuation API HTTP error: {e.response.status_code} - {e.response.text}")
            raise ValuationEngineError(
                f"Valuation API returned {e.response.status_code}: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Valuation API request error: {str(e)}")
            raise ValuationEngineError(f"Failed to connect to Valuation API: {str(e)}")
        except Exception as e:
            logger.error(f"Valuation API unexpected error: {str(e)}")
            raise ValuationEngineError(f"Unexpected error calling Valuation API: {str(e)}")

    async def _run_stub_valuation(
        self,
        normalized_financials: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> ValuationResponse:
        """
        Generate a stub/fake valuation for testing.

        Uses simple heuristics based on most recent year's financials.
        """
        logger.info("Running stub valuation (external API not configured)")

        # Extract most recent year's financials
        years = normalized_financials.get("years", [])
        if not years:
            # Return minimal stub
            return ValuationResponse(
                valuation_range=ValuationRange(
                    low=100000,
                    mid=250000,
                    high=500000,
                    currency="USD"
                ),
                multiples=ValuationMultiples(
                    sde_multiple_low=2.0,
                    sde_multiple_high=3.5,
                ),
                methodology="Stub Valuation - No Financials Provided",
                confidence_level="low",
                notes="This is a stub valuation for testing. No real financials were provided.",
                calculated_at=datetime.utcnow().isoformat(),
            )

        # Get most recent year
        most_recent = max(years, key=lambda y: y.get("year", 0))
        revenue = most_recent.get("revenue", 0)
        sde = most_recent.get("sde", 0)
        ebitda = most_recent.get("ebitda", 0)

        # Simple heuristics
        # Typical multiples for small businesses:
        # SDE: 2.0x - 3.5x
        # EBITDA: 3.0x - 5.0x
        # Revenue: 0.5x - 1.5x (for SaaS/tech)

        sde_multiple_low = 2.0
        sde_multiple_high = 3.5

        ebitda_multiple_low = 3.0
        ebitda_multiple_high = 5.0

        revenue_multiple_low = 0.5
        revenue_multiple_high = 1.5

        # Calculate ranges
        if sde > 0:
            val_low = sde * sde_multiple_low
            val_high = sde * sde_multiple_high
            val_mid = (val_low + val_high) / 2
        elif ebitda > 0:
            val_low = ebitda * ebitda_multiple_low
            val_high = ebitda * ebitda_multiple_high
            val_mid = (val_low + val_high) / 2
        elif revenue > 0:
            val_low = revenue * revenue_multiple_low
            val_high = revenue * revenue_multiple_high
            val_mid = (val_low + val_high) / 2
        else:
            val_low = 100000
            val_mid = 250000
            val_high = 500000

        return ValuationResponse(
            valuation_range=ValuationRange(
                low=round(val_low, 2),
                mid=round(val_mid, 2),
                high=round(val_high, 2),
                currency="USD"
            ),
            multiples=ValuationMultiples(
                sde_multiple_low=sde_multiple_low,
                sde_multiple_high=sde_multiple_high,
                ebitda_multiple_low=ebitda_multiple_low,
                ebitda_multiple_high=ebitda_multiple_high,
                revenue_multiple_low=revenue_multiple_low,
                revenue_multiple_high=revenue_multiple_high,
            ),
            methodology="Stub Valuation - Simple Multiples Heuristic",
            confidence_level="low",
            notes=(
                f"This is a stub valuation for testing purposes. "
                f"Based on {most_recent.get('year')} financials: "
                f"Revenue=${revenue:,.0f}, SDE=${sde:,.0f}, EBITDA=${ebitda:,.0f}. "
                f"Real valuation requires external API integration."
            ),
            calculated_at=datetime.utcnow().isoformat(),
        )

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the valuation engine is reachable.

        Returns:
            Dictionary with health status
        """
        if self.stub_mode:
            return {
                "status": "stub",
                "available": True,
                "message": "Running in stub mode",
            }

        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()

                return {
                    "status": "healthy",
                    "available": True,
                    "message": "Valuation engine is reachable",
                }

        except Exception as e:
            logger.warning(f"Valuation engine health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "available": False,
                "message": f"Failed to reach valuation engine: {str(e)}",
            }
