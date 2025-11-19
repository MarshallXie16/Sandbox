"""
Standard Valuation Flow API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Project, FinancialInputs
from app.models.project import ProjectType
from app.schemas.project import ProjectCreateStandard, ProjectResponse
from app.schemas.answer import AnswersSubmit, AnswerResponse
from app.schemas.score import ScoreResponse, StandardValuationResponse
from app.services.answer_service import save_answers, load_answers
from app.services.score_engine import compute_scorecard, get_score_summary
from app.services.standard_valuation import run_standard_valuation
from app.services.report_builder import generate_standard_report_markdown, save_report

router = APIRouter(prefix="/standard", tags=["Standard Valuation"])


@router.post("/projects", response_model=ProjectResponse, status_code=201)
def create_standard_project(
    project_data: ProjectCreateStandard,
    db: Session = Depends(get_db)
):
    """
    Create a new Standard valuation project
    Optionally includes financial inputs (3 years)
    Assigns questionnaire template
    """
    # Create project
    project = Project(
        name=project_data.name,
        project_type=ProjectType.STANDARD,
        industry=project_data.industry,
        description=project_data.description
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Create financial inputs (optional for Standard)
    if project_data.financial_inputs:
        for fin_input in project_data.financial_inputs:
            financial_input = FinancialInputs(
                project_id=project.id,
                year=fin_input.year,
                revenue=fin_input.revenue,
                net_profit=fin_input.net_profit,
                ebitda=fin_input.ebitda,
                total_assets=fin_input.total_assets,
                total_liabilities=fin_input.total_liabilities
            )
            db.add(financial_input)

        db.commit()

    db.refresh(project)
    return project


@router.post("/projects/{project_id}/answers")
def submit_answers(
    project_id: UUID,
    answers_data: AnswersSubmit,
    db: Session = Depends(get_db)
):
    """
    Save questionnaire answers for a Standard project
    """
    # Verify project exists and is Standard type
    project = db.query(Project).filter_by(id=project_id, project_type=ProjectType.STANDARD).first()
    if not project:
        raise HTTPException(status_code=404, detail="Standard project not found")

    try:
        answers = save_answers(db, project_id, [a.model_dump() for a in answers_data.answers])

        return {
            "project_id": str(project_id),
            "answers_saved": len(answers),
            "message": "Answers saved successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/projects/{project_id}/answers")
def get_answers(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Load all answers for a project
    """
    # Verify project exists
    project = db.query(Project).filter_by(id=project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        answers = load_answers(db, project_id)
        return {
            "project_id": str(project_id),
            "answers": answers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/projects/{project_id}/score", response_model=ScoreResponse)
def calculate_score(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Run scorecard computation for a Standard project
    Computes dimension scores and overall rating
    """
    # Verify project exists
    project = db.query(Project).filter_by(id=project_id, project_type=ProjectType.STANDARD).first()
    if not project:
        raise HTTPException(status_code=404, detail="Standard project not found")

    try:
        # Compute scorecard
        score_result = compute_scorecard(db, project_id)

        # Get formatted summary
        score_summary = get_score_summary(db, project_id)

        return score_summary
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/projects/{project_id}/valuation", response_model=StandardValuationResponse)
def calculate_standard_valuation(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Run Standard Valuation
    Applies scorecard adjustment to Quick valuation baseline
    """
    # Verify project exists
    project = db.query(Project).filter_by(id=project_id, project_type=ProjectType.STANDARD).first()
    if not project:
        raise HTTPException(status_code=404, detail="Standard project not found")

    try:
        result = run_standard_valuation(db, project_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/projects/{project_id}/report")
def generate_standard_report(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Generate Standard Valuation report (Exit Ready MPSP)
    """
    # Verify project exists
    project = db.query(Project).filter_by(id=project_id, project_type=ProjectType.STANDARD).first()
    if not project:
        raise HTTPException(status_code=404, detail="Standard project not found")

    try:
        # Generate report content
        content = generate_standard_report_markdown(db, project_id)

        # Save report
        report = save_report(db, project_id, "STANDARD_REPORT", content)

        return {
            "report_id": str(report.id),
            "project_id": str(project_id),
            "content": content,
            "format": "markdown"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_standard_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get Standard project details
    """
    project = db.query(Project).filter_by(id=project_id, project_type=ProjectType.STANDARD).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project
