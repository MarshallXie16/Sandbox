"""Quick Valuation Engine - Market-based valuation using industry multiples."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import UUID
from decimal import Decimal

from app.models.financial_input import FinancialInput
from app.models.valuation_summary import ValuationSummary
from app.models.project import Project


# Industry multiples (simplified version)
INDUSTRY_MULTIPLES = {
    "saas": {"sde": (3.0, 5.0, 7.0), "ebitda": (8.0, 12.0, 16.0)},
    "ecommerce": {"sde": (1.5, 2.5, 3.5), "ebitda": (5.0, 7.5, 10.0)},
    "manufacturing": {"sde": (1.5, 2.0, 2.5), "ebitda": (4.0, 6.5, 9.0)},
    "retail": {"sde": (1.0, 1.5, 2.0), "ebitda": (3.0, 5.0, 7.0)},
    "professional_services": {"sde": (1.5, 2.5, 3.5), "ebitda": (4.0, 6.0, 8.0)},
    "healthcare": {"sde": (2.0, 3.0, 4.0), "ebitda": (5.0, 7.5, 10.0)},
    "restaurant": {"sde": (1.0, 1.5, 2.0), "ebitda": (2.0, 3.5, 5.0)},
    "default": {"sde": (1.5, 2.5, 3.5), "ebitda": (4.0, 6.0, 8.0)},
}


async def compute_quick_valuation(
    db: AsyncSession,
    project_id: UUID,
    method: str = "sde_multiple"
) -> ValuationSummary:
    """
    Compute Quick Valuation using market multiples (industry × SDE/EBITDA).

    Args:
        db: Database session
        project_id: Project ID
        method: Valuation method ('sde_multiple', 'ebitda_multiple')

    Returns:
        ValuationSummary object
    """
    # Load project
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise ValueError(f"Project {project_id} not found")

    # Load most recent financial input
    result = await db.execute(
        select(FinancialInput)
        .where(FinancialInput.project_id == project_id)
        .order_by(FinancialInput.year.desc())
        .limit(1)
    )
    latest_financials = result.scalar_one_or_none()

    if not latest_financials:
        raise ValueError(f"No financial inputs found for project {project_id}")

    # Get industry multiples
    industry_key = project.industry.lower().replace(" ", "_")
    multiples = INDUSTRY_MULTIPLES.get(industry_key, INDUSTRY_MULTIPLES["default"])

    # Determine base metric and value
    if method == "sde_multiple":
        base_metric_type = "SDE"
        base_metric_value = latest_financials.sde or Decimal(0)
        multiple_low, multiple_mid, multiple_high = multiples["sde"]
    elif method == "ebitda_multiple":
        base_metric_type = "EBITDA"
        base_metric_value = latest_financials.ebitda or Decimal(0)
        multiple_low, multiple_mid, multiple_high = multiples["ebitda"]
    else:
        raise ValueError(f"Unknown valuation method: {method}")

    if base_metric_value <= 0:
        raise ValueError(
            f"Cannot value based on {base_metric_type} - value must be positive"
        )

    # Calculate valuation range
    value_low = base_metric_value * Decimal(str(multiple_low))
    value_mid = base_metric_value * Decimal(str(multiple_mid))
    value_high = base_metric_value * Decimal(str(multiple_high))

    # Delete existing valuation summary if any
    existing_result = await db.execute(
        select(ValuationSummary)
        .where(ValuationSummary.project_id == project_id)
    )
    existing_summary = existing_result.scalar_one_or_none()
    if existing_summary:
        await db.delete(existing_summary)

    # Create valuation summary
    summary = ValuationSummary(
        project_id=project_id,
        value_low=value_low,
        value_mid=value_mid,
        value_high=value_high,
        method=method,
        multiple_low=Decimal(str(multiple_low)),
        multiple_mid=Decimal(str(multiple_mid)),
        multiple_high=Decimal(str(multiple_high)),
        base_metric_value=base_metric_value,
        base_metric_type=base_metric_type,
        currency=project.currency,
        notes=f"Quick valuation using {method} for {project.industry} industry"
    )

    db.add(summary)
    await db.flush()

    return summary


async def get_valuation_summary(
    db: AsyncSession,
    project_id: UUID
) -> ValuationSummary:
    """Get valuation summary for a project."""
    result = await db.execute(
        select(ValuationSummary)
        .where(ValuationSummary.project_id == project_id)
    )
    summary = result.scalar_one_or_none()

    if not summary:
        raise ValueError(f"No valuation summary found for project {project_id}")

    return summary
