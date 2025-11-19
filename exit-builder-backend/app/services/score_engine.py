"""
Score Engine
Computes scorecard based on questionnaire answers and score rules
"""
from decimal import Decimal
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, List
from app.models import (
    Answer,
    ScoreDimension,
    ScoreRule,
    ScoreResult,
    ScoreDimensionResult,
    Question
)
from app.models.score import MatchType


def match_rule(answer: Answer, rule: ScoreRule) -> bool:
    """
    Check if an answer matches a score rule
    """
    if rule.match_type == MatchType.OPTION_VALUE:
        # Check if selected option value matches
        if answer.selected_option_values:
            return rule.match_value in answer.selected_option_values
        return False

    elif rule.match_type == MatchType.YES_NO:
        # Check yes/no answers
        if answer.selected_option_values:
            # Answer stored as ["YES"] or ["NO"]
            answer_value = answer.selected_option_values[0] if answer.selected_option_values else ""
            return answer_value == rule.match_value
        return False

    elif rule.match_type == MatchType.NUMERIC_RANGE:
        # Check numeric ranges
        if answer.value_numeric is None:
            return False

        value = float(answer.value_numeric)
        match_value = rule.match_value

        # Parse range patterns
        if match_value.startswith("<"):
            threshold = float(match_value[1:])
            return value < threshold
        elif match_value.startswith(">"):
            threshold = float(match_value[1:])
            return value > threshold
        elif "-" in match_value:
            parts = match_value.split("-")
            low = float(parts[0])
            high = float(parts[1])
            return low <= value <= high
        else:
            # Exact match
            return value == float(match_value)

    elif rule.match_type == MatchType.TEXT_CONTAINS:
        # Check if text contains substring
        if answer.value_text:
            return rule.match_value.lower() in answer.value_text.lower()
        return False

    return False


def compute_dimension_score(
    db: Session,
    project_id: UUID,
    dimension: ScoreDimension
) -> Dict:
    """
    Compute score for a specific dimension
    Returns score and contributing factors
    """
    # Get all rules for this dimension
    rules = db.query(ScoreRule).filter_by(dimension_id=dimension.id).all()

    total_score = 0
    matched_rules = []

    for rule in rules:
        # Get the answer for this rule's question
        answer = db.query(Answer).filter_by(
            project_id=project_id,
            question_id=rule.question_id
        ).first()

        if not answer:
            continue

        # Check if answer matches rule
        if match_rule(answer, rule):
            total_score += rule.score_delta
            matched_rules.append({
                "question_code": answer.question.code,
                "question_text": answer.question.text,
                "score_delta": rule.score_delta,
                "notes": rule.notes
            })

    return {
        "dimension_code": dimension.code,
        "dimension_name": dimension.name,
        "score": total_score,
        "weight": float(dimension.weight),
        "matched_rules": matched_rules
    }


def compute_scorecard(db: Session, project_id: UUID) -> ScoreResult:
    """
    Compute complete scorecard for a project

    Process:
    1. Load all answers
    2. For each dimension:
       - Find matching score rules
       - Sum deltas → dimension score
    3. Compute total_score = weighted sum of dimension scores
    4. Assign rating (A/B/C/D)
    5. Map rating → valuation_adjustment_factor
    6. Create score_results + score_dimension_results

    Returns:
        ScoreResult object
    """
    # Get all dimensions
    dimensions = db.query(ScoreDimension).all()

    if not dimensions:
        raise ValueError("No score dimensions found. Please run seed data.")

    dimension_results = []
    total_weighted_score = 0
    max_possible_score = 0

    for dimension in dimensions:
        dim_result = compute_dimension_score(db, project_id, dimension)
        dimension_results.append(dim_result)

        # Calculate weighted contribution
        # Assuming max score per dimension is around 35 points (adjust as needed)
        max_dim_score = 35
        max_possible_score += max_dim_score * float(dimension.weight)

        # Add weighted score
        total_weighted_score += dim_result["score"] * float(dimension.weight)

    # Normalize to 100 scale
    if max_possible_score > 0:
        total_score = int((total_weighted_score / max_possible_score) * 100)
    else:
        total_score = 0

    # Ensure score is within 0-100
    total_score = max(0, min(100, total_score))

    # Assign rating
    if total_score >= 80:
        rating = "A"
        adjustment_factor = Decimal("1.10")
    elif total_score >= 65:
        rating = "B"
        adjustment_factor = Decimal("1.00")
    elif total_score >= 50:
        rating = "C"
        adjustment_factor = Decimal("0.90")
    else:
        rating = "D"
        adjustment_factor = Decimal("0.80")

    # Create ScoreResult
    score_result = ScoreResult(
        project_id=project_id,
        total_score=total_score,
        rating=rating,
        valuation_adjustment_factor=adjustment_factor
    )
    db.add(score_result)
    db.commit()
    db.refresh(score_result)

    # Create ScoreDimensionResults
    for dim_result in dimension_results:
        dimension = db.query(ScoreDimension).filter_by(code=dim_result["dimension_code"]).first()

        # Generate comment based on score
        score = dim_result["score"]
        if score >= 25:
            comment = f"Strong performance in {dim_result['dimension_name']}"
        elif score >= 15:
            comment = f"Good performance in {dim_result['dimension_name']}"
        elif score >= 5:
            comment = f"Moderate performance in {dim_result['dimension_name']}"
        else:
            comment = f"Needs improvement in {dim_result['dimension_name']}"

        dim_score_result = ScoreDimensionResult(
            score_result_id=score_result.id,
            dimension_id=dimension.id,
            score=dim_result["score"],
            comment=comment
        )
        db.add(dim_score_result)

    db.commit()
    db.refresh(score_result)

    return score_result


def get_score_summary(db: Session, project_id: UUID) -> Dict:
    """
    Get formatted score summary for reporting
    """
    score_result = db.query(ScoreResult).filter_by(project_id=project_id).first()

    if not score_result:
        raise ValueError("No score result found. Please run compute_scorecard first.")

    # Get dimension results
    dimension_results = db.query(ScoreDimensionResult).filter_by(
        score_result_id=score_result.id
    ).all()

    dimensions_summary = []
    for dim_result in dimension_results:
        dimensions_summary.append({
            "code": dim_result.dimension.code,
            "name": dim_result.dimension.name,
            "score": dim_result.score,
            "weight": float(dim_result.dimension.weight),
            "comment": dim_result.comment
        })

    return {
        "total_score": score_result.total_score,
        "rating": score_result.rating,
        "adjustment_factor": float(score_result.valuation_adjustment_factor),
        "dimensions": dimensions_summary
    }
