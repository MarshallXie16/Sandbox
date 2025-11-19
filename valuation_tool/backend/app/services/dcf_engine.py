"""DCF Engine - Discounted Cash Flow valuation calculation."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import UUID
from decimal import Decimal

from app.models.dcf_parameter import DCFParameter
from app.models.dcf_cash_flow import DCFCashFlow
from app.models.dcf_result import DCFResult
from app.services.recast_engine import get_latest_normalized_metric


async def compute_dcf_valuation(
    db: AsyncSession,
    project_id: UUID
) -> DCFResult:
    """
    Compute DCF valuation for a project based on manually entered DCF parameters.

    Algorithm:
    1. Load DCF parameters
    2. Get base year normalized metric
    3. Load or generate projected cash flows
    4. Calculate present value of cash flows
    5. Calculate terminal value
    6. Calculate present value of terminal value
    7. Sum to get DCF equity value
    8. Store results in DCFResult

    Returns:
        DCFResult object
    """
    # Load DCF parameters
    result = await db.execute(
        select(DCFParameter)
        .where(DCFParameter.project_id == project_id)
    )
    params = result.scalar_one_or_none()

    if not params:
        raise ValueError(f"No DCF parameters found for project {project_id}")

    # Get base year metric
    base_year, base_value = await get_latest_normalized_metric(
        db, project_id, params.base_metric.lower()
    )

    # Load cash flows
    result = await db.execute(
        select(DCFCashFlow)
        .where(DCFCashFlow.project_id == project_id)
        .order_by(DCFCashFlow.year_index)
    )
    cash_flows = result.scalars().all()

    # If cash flows don't exist or count doesn't match projection years, we need them
    # For now, we'll assume cash flows were manually entered (as per spec)
    if len(cash_flows) != params.projection_years:
        # In a real implementation, you might auto-generate based on growth rates
        # For this version, we require explicit cash flows if use_explicit_cash_flows=True
        if params.use_explicit_cash_flows:
            raise ValueError(
                f"DCF parameters require {params.projection_years} cash flow projections, "
                f"but only {len(cash_flows)} were found"
            )

    # Calculate present value of each cash flow
    present_value_sum = Decimal(0)
    discount_rate = params.discount_rate

    for cf in cash_flows:
        # PV = CF / (1 + r)^n
        pv = cf.cash_flow / ((Decimal(1) + discount_rate) ** cf.year_index)
        cf.discounted_cash_flow = pv
        present_value_sum += pv
        db.add(cf)

    # Calculate terminal value
    last_cash_flow = cash_flows[-1].cash_flow if cash_flows else base_value

    if params.terminal_method == 'terminal_growth':
        # Gordon Growth Model: TV = CF_n * (1 + g) / (r - g)
        g = params.terminal_growth_rate or Decimal(0)
        if discount_rate <= g:
            raise ValueError(
                f"Discount rate ({discount_rate}) must be greater than "
                f"terminal growth rate ({g})"
            )
        terminal_value = (last_cash_flow * (Decimal(1) + g)) / (discount_rate - g)

    elif params.terminal_method == 'exit_multiple':
        # Exit Multiple: TV = CF_n * Multiple
        multiple = params.terminal_multiple or Decimal(0)
        terminal_value = last_cash_flow * multiple

    else:
        raise ValueError(f"Unknown terminal method: {params.terminal_method}")

    # Calculate present value of terminal value
    # PV_TV = TV / (1 + r)^n
    pv_terminal_value = terminal_value / (
        (Decimal(1) + discount_rate) ** params.projection_years
    )

    # Calculate total DCF equity value
    dcf_equity_value = present_value_sum + pv_terminal_value

    # Delete existing DCF result if any
    existing_result = await db.execute(
        select(DCFResult)
        .where(DCFResult.project_id == project_id)
    )
    existing_dcf = existing_result.scalar_one_or_none()
    if existing_dcf:
        await db.delete(existing_dcf)

    # Create new DCF result
    dcf_result = DCFResult(
        project_id=project_id,
        present_value_of_cash_flows=present_value_sum,
        terminal_value=terminal_value,
        present_value_of_terminal_value=pv_terminal_value,
        dcf_equity_value=dcf_equity_value,
        currency="CAD"  # Get from project
    )

    db.add(dcf_result)
    await db.flush()

    return dcf_result


async def get_dcf_result(
    db: AsyncSession,
    project_id: UUID
) -> DCFResult:
    """Get DCF result for a project."""
    result = await db.execute(
        select(DCFResult)
        .where(DCFResult.project_id == project_id)
    )
    dcf_result = result.scalar_one_or_none()

    if not dcf_result:
        raise ValueError(f"No DCF result found for project {project_id}")

    return dcf_result
