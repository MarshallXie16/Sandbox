"""
FastAPI routes for Exit Ready Automation.
"""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.workflow import CaseStatus, InvalidTransitionError
from app.schemas.case import (
    CaseCreate,
    CaseUpdate,
    CaseResponse,
    CaseSummary,
    CaseList,
    CaseIntakeData,
)
from app.schemas.document import DocResponse, DocChecklist
from app.schemas.event import EventResponse
from app.services import (
    CaseService,
    IntakeService,
    DocsService,
    ValuationService,
    DraftsService,
    DeliveryService,
    ExportService,
)

router = APIRouter(prefix="/exit-ready", tags=["exit-ready"])


# ==================== Case Management ====================

@router.post("/cases", response_model=CaseResponse, status_code=201)
async def create_case(
    case_data: CaseCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new Exit Ready case."""
    service = CaseService(db)
    return await service.create_case(case_data)


@router.get("/cases", response_model=CaseList)
async def list_cases(
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """List all Exit Ready cases with pagination."""
    service = CaseService(db)
    cases, total = await service.list_cases(status=status, page=page, page_size=page_size)

    total_pages = (total + page_size - 1) // page_size

    return CaseList(
        items=[CaseSummary.model_validate(c) for c in cases],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/cases/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: int,
    include_documents: bool = Query(False),
    include_events: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific case by ID."""
    service = CaseService(db)
    case = await service.get_case(
        case_id,
        include_documents=include_documents,
        include_events=include_events
    )

    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    return case


@router.patch("/cases/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: int,
    update_data: CaseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a case."""
    service = CaseService(db)
    case = await service.update_case(case_id, update_data)

    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    return case


@router.post("/cases/{case_id}/status")
async def update_case_status(
    case_id: int,
    new_status: CaseStatus,
    admin_override: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """Update case status (with workflow validation)."""
    service = CaseService(db)

    try:
        case = await service.update_status(
            case_id,
            new_status,
            admin_override=admin_override
        )
        return case

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/cases/{case_id}", status_code=204)
async def delete_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a case."""
    service = CaseService(db)
    deleted = await service.delete_case(case_id)

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")


# ==================== Intake ====================

@router.post("/cases/{case_id}/intake/send")
async def send_intake_link(
    case_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Send intake form link to seller."""
    service = IntakeService(db)

    try:
        result = await service.send_intake_link(case_id)
        return {"status": "sent", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/cases/{case_id}/intake/import")
async def import_intake_data(
    case_id: int,
    intake_data: CaseIntakeData,
    db: AsyncSession = Depends(get_db),
):
    """Import intake form responses."""
    service = IntakeService(db)

    try:
        result = await service.import_intake_data(
            case_id,
            intake_data.model_dump(exclude_none=True)
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== Documents ====================

@router.post("/cases/{case_id}/checklist", response_model=DocChecklist)
async def generate_checklist(
    case_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Generate document checklist for a case."""
    service = DocsService(db)

    try:
        return await service.generate_checklist(case_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/cases/{case_id}/checklist", response_model=DocChecklist)
async def get_checklist(
    case_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get document checklist for a case."""
    service = DocsService(db)
    return await service.get_checklist(case_id)


@router.post("/documents/{doc_id}/received", response_model=DocResponse)
async def mark_document_received(
    doc_id: int,
    file_url: str,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Mark a document as received."""
    service = DocsService(db)

    try:
        return await service.mark_document_received(doc_id, file_url, notes)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/documents/{doc_id}/waive", response_model=DocResponse)
async def waive_document(
    doc_id: int,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Waive a document requirement."""
    service = DocsService(db)

    try:
        return await service.waive_document(doc_id, notes)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== Valuation ====================

@router.post("/cases/{case_id}/valuation")
async def run_valuation(
    case_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Run valuation for a case."""
    service = ValuationService(db)

    try:
        result = await service.run_valuation(case_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Drafts ====================

@router.post("/cases/{case_id}/drafts")
async def generate_drafts(
    case_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Generate document drafts (teaser, summary, CIM)."""
    service = DraftsService(db)

    try:
        drafts = await service.generate_drafts(case_id)
        return {"status": "generated", "drafts": drafts}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/cases/{case_id}/drafts")
async def update_drafts(
    case_id: int,
    updated_drafts: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
):
    """Update drafts after human review."""
    service = DraftsService(db)

    try:
        drafts = await service.update_drafts(case_id, updated_drafts)
        return {"status": "updated", "drafts": drafts}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== Export & Delivery ====================

@router.post("/cases/{case_id}/export")
async def export_report(
    case_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Export Exit Ready report to PDF."""
    service = ExportService(db)

    try:
        report_url = await service.export_exit_ready_report(case_id)
        return {"status": "exported", "report_url": report_url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cases/{case_id}/deliver")
async def deliver_report(
    case_id: int,
    channel: str = Query("email", description="Delivery channel"),
    db: AsyncSession = Depends(get_db),
):
    """Deliver Exit Ready report to seller."""
    service = DeliveryService(db)

    try:
        result = await service.deliver_report(case_id, channel=channel)
        return {"status": "delivered", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cases/{case_id}/close")
async def close_case(
    case_id: int,
    next_step: str = Query("none"),
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Close an Exit Ready case."""
    service = DeliveryService(db)

    try:
        result = await service.close_case(case_id, next_step=next_step, notes=notes)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== Health & Stats ====================

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "exit-ready-automation"}


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get case statistics."""
    service = CaseService(db)
    return await service.get_stats()
