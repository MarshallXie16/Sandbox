"""
Quick Valuation Flow API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Project, FinancialInputs
from app.models.project import ProjectType
from app.schemas.project import ProjectCreateQuick, ProjectResponse, ValuationResponse
from app.services.quick_valuation import run_quick_valuation
from app.services.report_builder import generate_quick_report_markdown, save_report

router = APIRouter(prefix="/quick", tags=["Quick Valuation"])


@router.post("/projects", response_model=ProjectResponse, status_code=201)
def create_quick_project(
    project_data: ProjectCreateQuick,
    db: Session = Depends(get_db)
):
    """
    Create a new Quick valuation project with financial inputs
    """
    # Create project
    project = Project(
        name=project_data.name,
        project_type=ProjectType.QUICK,
        industry=project_data.industry,
        description=project_data.description
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Create financial inputs
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


@router.post("/projects/{project_id}/valuation", response_model=ValuationResponse)
def calculate_quick_valuation(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Run Quick Valuation for a project
    """
    try:
        result = run_quick_valuation(db, project_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/projects/{project_id}/report")
def generate_quick_report(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Generate Quick Valuation report
    """
    try:
        # Generate report content
        content = generate_quick_report_markdown(db, project_id)

        # Save report
        report = save_report(db, project_id, "QUICK_REPORT", content)

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
def get_quick_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get Quick project details
    """
    project = db.query(Project).filter_by(id=project_id, project_type=ProjectType.QUICK).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project
