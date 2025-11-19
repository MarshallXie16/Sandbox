"""API endpoints for Report generation."""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.services.report_generator import generate_full_valuation_report

router = APIRouter()


@router.get("/projects/{project_id}/full-valuation-report")
async def get_full_valuation_report(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Generate Full Valuation Report in Markdown format."""
    try:
        report = await generate_full_valuation_report(db, project_id)
        return Response(
            content=report,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f'inline; filename="valuation_report_{project_id}.md"'
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
