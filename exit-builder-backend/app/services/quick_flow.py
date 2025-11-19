"""
Quick Flow service - orchestrates the entire Quick Valuation workflow
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models import Client, Project, FinancialInput
from app.services.valuation_core import run_quick_valuation
from app.services.report_builder import generate_quick_report_markdown


# Pydantic models for request/response
class ClientPayload(BaseModel):
    """Client information payload"""
    id: Optional[UUID] = None
    name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class ProjectPayload(BaseModel):
    """Project information payload"""
    business_name: str
    industry_code: str
    location: Optional[str] = None


class FinancialPayload(BaseModel):
    """Financial information payload"""
    metric_type: str = Field(..., pattern="^(SDE|EBITDA)$")
    metric_value: float = Field(..., gt=0)
    revenue: float = Field(..., gt=0)


class QuickProjectPayload(BaseModel):
    """Complete payload for Quick Valuation flow"""
    client: ClientPayload
    project: ProjectPayload
    financial: FinancialPayload


class ValuationSummaryResponse(BaseModel):
    """Valuation summary response"""
    recommended_value_low: float
    recommended_value_mid: float
    recommended_value_high: float
    currency: str


class QuickFlowResponse(BaseModel):
    """Quick flow response"""
    project_id: UUID
    client_id: UUID
    report_id: UUID
    valuation_summary: ValuationSummaryResponse


def run_quick_flow(db: Session, payload: QuickProjectPayload) -> QuickFlowResponse:
    """
    Execute the complete Quick Valuation flow

    Steps:
    1. Create or retrieve client
    2. Create quick project
    3. Store financial inputs
    4. Run valuation
    5. Generate report

    Args:
        db: Database session
        payload: Quick project payload

    Returns:
        QuickFlowResponse: Complete response with IDs and valuation summary

    Raises:
        ValueError: If validation fails
        Exception: For other errors
    """
    try:
        # Step 1: Create or retrieve client
        if payload.client.id:
            client = db.query(Client).filter(Client.id == payload.client.id).first()
            if not client:
                raise ValueError(f"Client not found: {payload.client.id}")
        else:
            client = Client(
                name=payload.client.name,
                contact_name=payload.client.contact_name,
                email=payload.client.email,
                phone=payload.client.phone
            )
            db.add(client)
            db.flush()  # Get the ID without committing

        # Step 2: Create quick project
        project = Project(
            client_id=client.id,
            business_name=payload.project.business_name,
            industry_code=payload.project.industry_code,
            location=payload.project.location,
            project_type='quick',
            status='draft'
        )
        db.add(project)
        db.flush()

        # Step 3: Store financial inputs
        financial_input = FinancialInput(
            project_id=project.id,
            year=0,  # TTM (Trailing Twelve Months)
            revenue=payload.financial.revenue,
            sde=payload.financial.metric_value if payload.financial.metric_type == 'SDE' else None,
            ebitda=payload.financial.metric_value if payload.financial.metric_type == 'EBITDA' else None
        )
        db.add(financial_input)
        db.commit()

        # Step 4: Run valuation
        valuation_summary = run_quick_valuation(db, project.id)

        # Step 5: Generate report
        report_id = generate_quick_report_markdown(db, project.id)

        # Build response
        response = QuickFlowResponse(
            project_id=project.id,
            client_id=client.id,
            report_id=UUID(report_id),
            valuation_summary=ValuationSummaryResponse(
                recommended_value_low=float(valuation_summary.recommended_value_low),
                recommended_value_mid=float(valuation_summary.recommended_value_mid),
                recommended_value_high=float(valuation_summary.recommended_value_high),
                currency=valuation_summary.currency
            )
        )

        return response

    except Exception as e:
        db.rollback()
        raise e


def get_project_details(db: Session, project_id: UUID) -> Optional[dict]:
    """
    Get complete project details including client, financials, and valuation

    Args:
        db: Database session
        project_id: UUID of the project

    Returns:
        dict: Project details or None if not found
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None

    client = db.query(Client).filter(Client.id == project.client_id).first()
    financial = db.query(FinancialInput).filter(
        FinancialInput.project_id == project_id
    ).first()

    from app.services.valuation_core import get_valuation_summary
    valuation = get_valuation_summary(db, project_id)

    return {
        "project": {
            "id": str(project.id),
            "business_name": project.business_name,
            "industry_code": project.industry_code,
            "location": project.location,
            "project_type": project.project_type,
            "status": project.status,
            "created_at": project.created_at.isoformat() if project.created_at else None
        },
        "client": {
            "id": str(client.id),
            "name": client.name,
            "contact_name": client.contact_name,
            "email": client.email,
            "phone": client.phone
        } if client else None,
        "financial": {
            "revenue": float(financial.revenue) if financial.revenue else None,
            "sde": float(financial.sde) if financial and financial.sde else None,
            "ebitda": float(financial.ebitda) if financial and financial.ebitda else None
        } if financial else None,
        "valuation": {
            "recommended_value_low": float(valuation.recommended_value_low),
            "recommended_value_mid": float(valuation.recommended_value_mid),
            "recommended_value_high": float(valuation.recommended_value_high),
            "currency": valuation.currency
        } if valuation else None
    }
