"""
Quick Valuation Service
Handles simple financial-input-based valuation
"""
from decimal import Decimal
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, List
from app.models import Project, FinancialInputs, ValuationResults, ValuationSummary


# Industry multipliers for Quick Valuation
INDUSTRY_MULTIPLIERS = {
    "saas": {"revenue": 6.0, "ebitda": 12.0},
    "ecommerce": {"revenue": 2.5, "ebitda": 7.0},
    "professional_services": {"revenue": 1.5, "ebitda": 5.0},
    "manufacturing": {"revenue": 1.5, "ebitda": 6.0},
    "retail": {"revenue": 0.8, "ebitda": 5.0},
    "restaurant": {"revenue": 0.6, "ebitda": 3.5},
    "healthcare": {"revenue": 1.8, "ebitda": 7.0},
    "construction": {"revenue": 1.2, "ebitda": 5.0},
    "technology": {"revenue": 5.0, "ebitda": 10.0},
    "consulting": {"revenue": 1.8, "ebitda": 4.5},
}


def calculate_revenue_multiple_valuation(
    revenue: Decimal,
    industry: str
) -> Dict:
    """
    Calculate valuation using revenue multiple method
    """
    multipliers = INDUSTRY_MULTIPLIERS.get(industry.lower(), {"revenue": 2.0, "ebitda": 5.0})
    revenue_multiple = Decimal(str(multipliers["revenue"]))

    value = revenue * revenue_multiple

    return {
        "method": "revenue_multiple",
        "value": value,
        "confidence": "medium",
        "notes": f"Revenue ${revenue:,.2f} × {revenue_multiple}x multiple"
    }


def calculate_ebitda_multiple_valuation(
    ebitda: Decimal,
    industry: str
) -> Dict:
    """
    Calculate valuation using EBITDA multiple method
    """
    if ebitda <= 0:
        return {
            "method": "ebitda_multiple",
            "value": Decimal(0),
            "confidence": "low",
            "notes": "EBITDA is negative or zero - method not applicable"
        }

    multipliers = INDUSTRY_MULTIPLIERS.get(industry.lower(), {"revenue": 2.0, "ebitda": 5.0})
    ebitda_multiple = Decimal(str(multipliers["ebitda"]))

    value = ebitda * ebitda_multiple

    return {
        "method": "ebitda_multiple",
        "value": value,
        "confidence": "high",
        "notes": f"EBITDA ${ebitda:,.2f} × {ebitda_multiple}x multiple"
    }


def calculate_asset_based_valuation(
    total_assets: Decimal,
    total_liabilities: Decimal
) -> Dict:
    """
    Calculate valuation using asset-based method
    """
    net_assets = total_assets - total_liabilities
    asset_multiplier = Decimal("1.0")  # Book value

    if net_assets <= 0:
        return {
            "method": "asset_based",
            "value": Decimal(0),
            "confidence": "low",
            "notes": "Net assets are negative"
        }

    value = net_assets * asset_multiplier

    return {
        "method": "asset_based",
        "value": value,
        "confidence": "medium",
        "notes": f"Net assets ${net_assets:,.2f} × {asset_multiplier}x"
    }


def run_quick_valuation(db: Session, project_id: UUID) -> Dict:
    """
    Execute Quick Valuation flow
    Returns valuation summary with low, mid, high estimates
    """
    # Get project
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise ValueError(f"Project {project_id} not found")

    # Get most recent financial inputs (year 0)
    financial_input = db.query(FinancialInputs).filter_by(
        project_id=project_id,
        year=0
    ).first()

    if not financial_input or not financial_input.revenue:
        raise ValueError("Financial inputs (revenue) required for valuation")

    industry = project.industry or "technology"
    results = []

    # Calculate revenue multiple
    if financial_input.revenue:
        revenue_result = calculate_revenue_multiple_valuation(
            financial_input.revenue,
            industry
        )
        results.append(revenue_result)

        # Save to database
        valuation_result = ValuationResults(
            project_id=project_id,
            **revenue_result
        )
        db.add(valuation_result)

    # Calculate EBITDA multiple
    if financial_input.ebitda and financial_input.ebitda > 0:
        ebitda_result = calculate_ebitda_multiple_valuation(
            financial_input.ebitda,
            industry
        )
        results.append(ebitda_result)

        # Save to database
        valuation_result = ValuationResults(
            project_id=project_id,
            **ebitda_result
        )
        db.add(valuation_result)

    # Calculate asset-based
    if financial_input.total_assets and financial_input.total_liabilities:
        asset_result = calculate_asset_based_valuation(
            financial_input.total_assets,
            financial_input.total_liabilities
        )
        results.append(asset_result)

        # Save to database
        valuation_result = ValuationResults(
            project_id=project_id,
            **asset_result
        )
        db.add(valuation_result)

    # Calculate summary (low, mid, high)
    if not results:
        raise ValueError("No valid valuation methods available")

    values = [r["value"] for r in results if r["value"] > 0]

    if not values:
        raise ValueError("All valuation methods returned zero")

    value_low = min(values)
    value_high = max(values)
    value_mid = sum(values) / len(values)

    # Determine primary method (highest confidence)
    high_confidence_results = [r for r in results if r["confidence"] == "high"]
    primary_method = high_confidence_results[0]["method"] if high_confidence_results else results[0]["method"]

    # Save or update valuation summary
    summary = db.query(ValuationSummary).filter_by(project_id=project_id).first()
    if summary:
        summary.value_low = value_low
        summary.value_mid = value_mid
        summary.value_high = value_high
        summary.primary_method = primary_method
        summary.adjustment_factor = Decimal("1.0")
    else:
        summary = ValuationSummary(
            project_id=project_id,
            value_low=value_low,
            value_mid=value_mid,
            value_high=value_high,
            primary_method=primary_method,
            adjustment_factor=Decimal("1.0")
        )
        db.add(summary)

    db.commit()
    db.refresh(summary)

    return {
        "project_id": str(project_id),
        "value_low": float(summary.value_low),
        "value_mid": float(summary.value_mid),
        "value_high": float(summary.value_high),
        "primary_method": summary.primary_method,
        "results": results
    }
