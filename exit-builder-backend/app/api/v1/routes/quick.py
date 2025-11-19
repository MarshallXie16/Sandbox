"""
Quick Valuation API endpoints
"""
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.quick_flow import (
    run_quick_flow,
    get_project_details,
    QuickProjectPayload,
    QuickFlowResponse
)
from app.services.report_builder import get_report_content

router = APIRouter(prefix="/projects", tags=["Quick Valuation"])


@router.post("/quick", response_model=QuickFlowResponse, status_code=status.HTTP_201_CREATED)
def create_quick_project(
    payload: QuickProjectPayload,
    db: Session = Depends(get_db)
):
    """
    Create a Quick Valuation project

    This endpoint:
    - Creates or retrieves a client
    - Creates a new quick valuation project
    - Stores financial inputs
    - Runs the valuation calculation
    - Generates a Quick Summary report

    Returns:
    - project_id: UUID of the created project
    - client_id: UUID of the client
    - report_id: UUID of the generated report
    - valuation_summary: Estimated value range
    """
    try:
        result = run_quick_flow(db, payload)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{project_id}")
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get project details including client, financials, and valuation

    Args:
        project_id: UUID of the project

    Returns:
        Complete project details
    """
    project_details = get_project_details(db, project_id)

    if not project_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found: {project_id}"
        )

    return project_details


@router.get("/{project_id}/report")
def get_project_report(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get the latest report for a project

    Args:
        project_id: UUID of the project

    Returns:
        Markdown content of the report
    """
    from app.models import Report

    # Get the most recent report for this project
    report = db.query(Report).filter(
        Report.project_id == project_id
    ).order_by(Report.created_at.desc()).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No report found for project: {project_id}"
        )

    return {
        "report_id": str(report.id),
        "title": report.title,
        "status": report.status,
        "created_at": report.created_at.isoformat(),
        "content": report.content_markdown
    }
