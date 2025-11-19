"""Recast Engine - Compute normalized financials from financial inputs and normalization entries."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, UUID
from decimal import Decimal

from app.models.financial_input import FinancialInput
from app.models.normalization_entry import NormalizationEntry
from app.models.normalized_financial import NormalizedFinancial


async def recompute_normalized_financials(
    db: AsyncSession,
    project_id: UUID
) -> List[NormalizedFinancial]:
    """
    Rebuild normalized_financials for the given project from financial_inputs and normalization_entries.

    Algorithm:
    1. Load all financial_inputs for the project
    2. Load all normalization_entries for the project
    3. For each year in financial_inputs:
        - Start with reported financials
        - Apply normalization entries (addbacks/reductions)
        - Create/update NormalizedFinancial record

    Returns:
        List of NormalizedFinancial objects
    """
    # Load financial inputs
    result = await db.execute(
        select(FinancialInput)
        .where(FinancialInput.project_id == project_id)
        .order_by(FinancialInput.year)
    )
    financial_inputs = result.scalars().all()

    if not financial_inputs:
        return []

    # Load normalization entries
    result = await db.execute(
        select(NormalizationEntry)
        .where(NormalizationEntry.project_id == project_id)
    )
    normalization_entries = result.scalars().all()

    # Group normalization entries by year
    entries_by_year = {}
    for entry in normalization_entries:
        if entry.year not in entries_by_year:
            entries_by_year[entry.year] = []
        entries_by_year[entry.year].append(entry)

    # Delete existing normalized financials for this project
    existing_result = await db.execute(
        select(NormalizedFinancial)
        .where(NormalizedFinancial.project_id == project_id)
    )
    existing_normalized = existing_result.scalars().all()
    for nf in existing_normalized:
        await db.delete(nf)

    # Compute normalized financials for each year
    normalized_financials = []

    for fi in financial_inputs:
        year = fi.year

        # Start with reported values
        normalized_revenue = fi.revenue or Decimal(0)
        normalized_ebitda = fi.ebitda or Decimal(0)
        normalized_sde = fi.sde or Decimal(0)
        normalized_net_income = fi.net_income or Decimal(0)

        # Apply normalization entries for this year
        if year in entries_by_year:
            for entry in entries_by_year[year]:
                # Addbacks increase earnings (positive adjustment)
                # Reductions decrease earnings (negative adjustment)
                adjustment = entry.amount if entry.is_addback else -entry.amount

                # Apply to all earnings metrics
                # (In a more sophisticated system, you might apply category-specific adjustments)
                normalized_ebitda += adjustment
                normalized_sde += adjustment
                normalized_net_income += adjustment

        # Create normalized financial record
        nf = NormalizedFinancial(
            project_id=project_id,
            year=year,
            normalized_revenue=normalized_revenue,
            normalized_ebitda=normalized_ebitda,
            normalized_sde=normalized_sde,
            normalized_net_income=normalized_net_income,
            notes=f"Normalized financials for {year}"
        )

        db.add(nf)
        normalized_financials.append(nf)

    await db.flush()

    return normalized_financials


async def get_normalized_financials(
    db: AsyncSession,
    project_id: UUID
) -> List[NormalizedFinancial]:
    """Get all normalized financials for a project."""
    result = await db.execute(
        select(NormalizedFinancial)
        .where(NormalizedFinancial.project_id == project_id)
        .order_by(NormalizedFinancial.year)
    )
    return result.scalars().all()


async def get_latest_normalized_metric(
    db: AsyncSession,
    project_id: UUID,
    metric: str = "sde"
) -> tuple[int, Decimal]:
    """
    Get the latest year's normalized metric value.

    Args:
        db: Database session
        project_id: Project ID
        metric: Metric name ('sde', 'ebitda', 'net_income')

    Returns:
        Tuple of (year, value)
    """
    result = await db.execute(
        select(NormalizedFinancial)
        .where(NormalizedFinancial.project_id == project_id)
        .order_by(NormalizedFinancial.year.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()

    if not latest:
        raise ValueError(f"No normalized financials found for project {project_id}")

    if metric == "sde":
        return latest.year, latest.normalized_sde or Decimal(0)
    elif metric == "ebitda":
        return latest.year, latest.normalized_ebitda or Decimal(0)
    elif metric == "net_income":
        return latest.year, latest.normalized_net_income or Decimal(0)
    else:
        raise ValueError(f"Unknown metric: {metric}")
