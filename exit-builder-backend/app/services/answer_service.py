"""
Answer Service
Handles saving and loading questionnaire answers
"""
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict
from app.models import Answer, Question


def save_answers(db: Session, project_id: UUID, answers_data: List[Dict]) -> List[Answer]:
    """
    Save or update answers for a project

    Args:
        db: Database session
        project_id: Project ID
        answers_data: List of answer dictionaries with structure:
            {
                "question_code": str,
                "value_text": str (optional),
                "value_numeric": float (optional),
                "selected_option_values": list (optional)
            }

    Returns:
        List of saved Answer objects
    """
    saved_answers = []

    for answer_data in answers_data:
        question_code = answer_data.get("question_code")

        # Find question by code
        question = db.query(Question).filter_by(code=question_code).first()
        if not question:
            raise ValueError(f"Question with code '{question_code}' not found")

        # Check if answer already exists
        existing_answer = db.query(Answer).filter_by(
            project_id=project_id,
            question_id=question.id
        ).first()

        if existing_answer:
            # Update existing answer
            existing_answer.value_text = answer_data.get("value_text")
            existing_answer.value_numeric = answer_data.get("value_numeric")
            existing_answer.selected_option_values = answer_data.get("selected_option_values")
            saved_answers.append(existing_answer)
        else:
            # Create new answer
            new_answer = Answer(
                project_id=project_id,
                question_id=question.id,
                value_text=answer_data.get("value_text"),
                value_numeric=answer_data.get("value_numeric"),
                selected_option_values=answer_data.get("selected_option_values")
            )
            db.add(new_answer)
            saved_answers.append(new_answer)

    db.commit()

    # Refresh all answers
    for answer in saved_answers:
        db.refresh(answer)

    return saved_answers


def load_answers(db: Session, project_id: UUID) -> List[Dict]:
    """
    Load all answers for a project

    Returns:
        List of answer dictionaries with question details
    """
    answers = db.query(Answer).filter_by(project_id=project_id).all()

    result = []
    for answer in answers:
        result.append({
            "id": str(answer.id),
            "question_id": str(answer.question_id),
            "question_code": answer.question.code,
            "question_text": answer.question.text,
            "question_section": answer.question.section,
            "input_type": answer.question.input_type.value,
            "value_text": answer.value_text,
            "value_numeric": float(answer.value_numeric) if answer.value_numeric else None,
            "selected_option_values": answer.selected_option_values,
            "created_at": answer.created_at.isoformat(),
            "updated_at": answer.updated_at.isoformat()
        })

    return result


def get_answer_by_question_code(db: Session, project_id: UUID, question_code: str) -> Answer:
    """
    Get a specific answer by question code
    """
    question = db.query(Question).filter_by(code=question_code).first()
    if not question:
        return None

    answer = db.query(Answer).filter_by(
        project_id=project_id,
        question_id=question.id
    ).first()

    return answer
