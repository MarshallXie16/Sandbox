"""
Core valuation logic for Quick Valuation flow
"""
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import (
    Project,
    FinancialInput,
    IndustryMultiple,
    ValuationMethod,
    ValuationInput,
    ValuationResult,
    ValuationSummary
)


class ValuationError(Exception):
    """Custom exception for valuation errors"""
    pass


def run_quick_valuation(db: Session, project_id: UUID) -> ValuationSummary:
    """
    Run Quick Valuation for a project

    Algorithm:
    1. Load project + financial_inputs
    2. Determine metric type: SDE or EBITDA
    3. Lookup industry_multiples
    4. Compute value_low/mid/high = metric_value * multiple_low/mid/high
    5. Create valuation_inputs + valuation_results
    6. Update/Create valuation_summary

    Args:
        db: Database session
        project_id: UUID of the project

    Returns:
        ValuationSummary: The computed valuation summary

    Raises:
        ValuationError: If required data is missing or invalid
    """
    # Step 1: Load project and financial inputs
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValuationError(f"Project not found: {project_id}")

    financial_input = db.query(FinancialInput).filter(
        FinancialInput.project_id == project_id
    ).first()

    if not financial_input:
        raise ValuationError(f"No financial inputs found for project: {project_id}")

    # Step 2: Determine metric type
    if financial_input.sde is not None:
        metric_type = "SDE"
        metric_value = financial_input.sde
    elif financial_input.ebitda is not None:
        metric_type = "EBITDA"
        metric_value = financial_input.ebitda
    else:
        raise ValuationError("Either SDE or EBITDA must be provided")

    # Step 3: Lookup industry multiples
    industry_multiple = db.query(IndustryMultiple).filter(
        IndustryMultiple.industry_code == project.industry_code,
        IndustryMultiple.metric_type == metric_type
    ).first()

    if not industry_multiple:
        raise ValuationError(
            f"No industry multiples found for industry {project.industry_code} "
            f"and metric type {metric_type}"
        )

    # Optional: Check revenue size range if specified
    if industry_multiple.size_min_revenue or industry_multiple.size_max_revenue:
        revenue = financial_input.revenue
        if industry_multiple.size_min_revenue and revenue < industry_multiple.size_min_revenue:
            print(f"Warning: Revenue {revenue} is below minimum {industry_multiple.size_min_revenue}")
        if industry_multiple.size_max_revenue and revenue > industry_multiple.size_max_revenue:
            print(f"Warning: Revenue {revenue} is above maximum {industry_multiple.size_max_revenue}")

    # Step 4: Compute valuations
    value_low = Decimal(str(metric_value)) * Decimal(str(industry_multiple.multiple_low))
    value_mid = Decimal(str(metric_value)) * Decimal(str(industry_multiple.multiple_mid))
    value_high = Decimal(str(metric_value)) * Decimal(str(industry_multiple.multiple_high))

    # Get valuation method
    method_code = f"{metric_type}_MULTIPLE"
    valuation_method = db.query(ValuationMethod).filter(
        ValuationMethod.code == method_code
    ).first()

    if not valuation_method:
        raise ValuationError(f"Valuation method not found: {method_code}")

    # Step 5: Create valuation_inputs
    valuation_input = ValuationInput(
        project_id=project_id,
        valuation_method_id=valuation_method.id,
        base_metric=metric_type,
        base_metric_value=metric_value,
        base_multiple=industry_multiple.multiple_mid,
        adjusted_multiple=industry_multiple.multiple_mid,  # Same for Quick MVP
        notes=f"Using {industry_multiple.source or 'market data'}"
    )
    db.add(valuation_input)

    # Create valuation_results
    valuation_result = ValuationResult(
        project_id=project_id,
        valuation_method_id=valuation_method.id,
        scenario='base',
        value_low=value_low,
        value_mid=value_mid,
        value_high=value_high,
        currency='CAD'
    )
    db.add(valuation_result)

    # Step 6: Update or create valuation_summary
    existing_summary = db.query(ValuationSummary).filter(
        ValuationSummary.project_id == project_id
    ).first()

    if existing_summary:
        existing_summary.recommended_value_low = value_low
        existing_summary.recommended_value_mid = value_mid
        existing_summary.recommended_value_high = value_high
        existing_summary.notes = f"Quick valuation using {metric_type} multiple method"
        summary = existing_summary
    else:
        summary = ValuationSummary(
            project_id=project_id,
            recommended_value_low=value_low,
            recommended_value_mid=value_mid,
            recommended_value_high=value_high,
            currency='CAD',
            notes=f"Quick valuation using {metric_type} multiple method"
        )
        db.add(summary)

    # Update project status
    project.status = 'in_analysis'

    db.commit()
    db.refresh(summary)

    return summary


def get_valuation_summary(db: Session, project_id: UUID) -> Optional[ValuationSummary]:
    """
    Get the valuation summary for a project

    Args:
        db: Database session
        project_id: UUID of the project

    Returns:
        ValuationSummary or None if not found
    """
    return db.query(ValuationSummary).filter(
        ValuationSummary.project_id == project_id
    ).first()
