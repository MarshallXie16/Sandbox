"""Full Valuation Engine - Weighted valuation combining Market, DCF, and Asset approaches."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import UUID, Optional
from decimal import Decimal

from app.models.full_valuation_summary import FullValuationSummary
from app.models.valuation_summary import ValuationSummary
from app.models.dcf_result import DCFResult
from app.models.project import Project


async def compute_full_valuation(
    db: AsyncSession,
    project_id: UUID,
    weight_market: Decimal,
    weight_dcf: Decimal,
    weight_asset: Decimal,
    asset_value: Optional[Decimal] = None
) -> FullValuationSummary:
    """
    Compute weighted final valuation combining Market, DCF, and Asset approaches.

    Args:
        db: Database session
        project_id: Project ID
        weight_market: Weight for market approach (e.g., 0.6 = 60%)
        weight_dcf: Weight for DCF approach (e.g., 0.3 = 30%)
        weight_asset: Weight for asset approach (e.g., 0.1 = 10%)
        asset_value: Optional manually entered asset-based value

    Returns:
        FullValuationSummary object
    """
    # Validate weights sum to approximately 1.0
    total_weight = weight_market + weight_dcf + weight_asset
    if abs(total_weight - Decimal(1)) > Decimal("0.01"):
        raise ValueError(
            f"Weights must sum to 1.0 (got {total_weight}). "
            f"Market: {weight_market}, DCF: {weight_dcf}, Asset: {weight_asset}"
        )

    # Load project
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise ValueError(f"Project {project_id} not found")

    # Load market valuation summary
    result = await db.execute(
        select(ValuationSummary)
        .where(ValuationSummary.project_id == project_id)
    )
    market_summary = result.scalar_one_or_none()

    # Load DCF result
    result = await db.execute(
        select(DCFResult)
        .where(DCFResult.project_id == project_id)
    )
    dcf_result = result.scalar_one_or_none()

    # Get values (use None if not available)
    market_value_mid = market_summary.value_mid if market_summary else None
    dcf_value = dcf_result.dcf_equity_value if dcf_result else None

    # Calculate weighted mid value
    weighted_mid = Decimal(0)

    if market_value_mid and weight_market > 0:
        weighted_mid += market_value_mid * weight_market

    if dcf_value and weight_dcf > 0:
        weighted_mid += dcf_value * weight_dcf

    if asset_value and weight_asset > 0:
        weighted_mid += asset_value * weight_asset

    # Calculate range (±20% for simplicity)
    range_factor = Decimal("0.20")
    final_value_low = weighted_mid * (Decimal(1) - range_factor)
    final_value_mid = weighted_mid
    final_value_high = weighted_mid * (Decimal(1) + range_factor)

    # Delete existing full valuation summary if any
    existing_result = await db.execute(
        select(FullValuationSummary)
        .where(FullValuationSummary.project_id == project_id)
    )
    existing_summary = existing_result.scalar_one_or_none()
    if existing_summary:
        await db.delete(existing_summary)

    # Create full valuation summary
    summary = FullValuationSummary(
        project_id=project_id,
        market_value_mid=market_value_mid,
        dcf_value=dcf_value,
        asset_value=asset_value,
        weight_market=weight_market,
        weight_dcf=weight_dcf,
        weight_asset=weight_asset,
        final_value_low=final_value_low,
        final_value_mid=final_value_mid,
        final_value_high=final_value_high,
        currency=project.currency,
        notes="Weighted valuation combining Market, DCF, and Asset approaches"
    )

    db.add(summary)
    await db.flush()

    return summary


async def get_full_valuation_summary(
    db: AsyncSession,
    project_id: UUID
) -> FullValuationSummary:
    """Get full valuation summary for a project."""
    result = await db.execute(
        select(FullValuationSummary)
        .where(FullValuationSummary.project_id == project_id)
    )
    summary = result.scalar_one_or_none()

    if not summary:
        raise ValueError(f"No full valuation summary found for project {project_id}")

    return summary
