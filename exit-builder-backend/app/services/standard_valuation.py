"""
Standard Valuation Service
Applies scorecard adjustment to Quick Valuation
"""
from decimal import Decimal
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict
from app.models import ValuationSummary, ScoreResult
from app.services.quick_valuation import run_quick_valuation


def run_standard_valuation(db: Session, project_id: UUID) -> Dict:
    """
    Execute Standard Valuation flow

    Process:
    1. Run Quick Valuation to get baseline
    2. Load score_results (if missing, raise exception)
    3. Apply valuation_adjustment_factor to value_low, value_mid, value_high
    4. Update valuation_summary with adjusted values

    Returns:
        Valuation summary with adjustment applied
    """
    # Step 1: Run Quick Valuation (or verify it exists)
    summary = db.query(ValuationSummary).filter_by(project_id=project_id).first()

    if not summary:
        # Run quick valuation to establish baseline
        run_quick_valuation(db, project_id)
        summary = db.query(ValuationSummary).filter_by(project_id=project_id).first()

    if not summary:
        raise ValueError("Could not generate baseline valuation")

    # Step 2: Load score results
    score_result = db.query(ScoreResult).filter_by(project_id=project_id).first()

    if not score_result:
        raise ValueError(
            "No score result found. Please run compute_scorecard first."
        )

    # Step 3: Apply adjustment factor
    adjustment = score_result.valuation_adjustment_factor

    # Store original baseline values (for reference)
    baseline_low = summary.value_low
    baseline_mid = summary.value_mid
    baseline_high = summary.value_high

    # Apply adjustment
    adjusted_low = baseline_low * adjustment
    adjusted_mid = baseline_mid * adjustment
    adjusted_high = baseline_high * adjustment

    # Step 4: Update summary
    summary.value_low = adjusted_low
    summary.value_mid = adjusted_mid
    summary.value_high = adjusted_high
    summary.adjustment_factor = adjustment

    db.commit()
    db.refresh(summary)

    return {
        "project_id": str(project_id),
        "baseline_valuation": {
            "value_low": float(baseline_low),
            "value_mid": float(baseline_mid),
            "value_high": float(baseline_high)
        },
        "score": {
            "total_score": score_result.total_score,
            "rating": score_result.rating,
            "adjustment_factor": float(adjustment)
        },
        "adjusted_valuation": {
            "value_low": float(adjusted_low),
            "value_mid": float(adjusted_mid),
            "value_high": float(adjusted_high)
        },
        "primary_method": summary.primary_method
    }
