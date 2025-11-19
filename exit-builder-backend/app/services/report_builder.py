"""
Report builder service - generates Markdown reports
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import (
    Project,
    Client,
    FinancialInput,
    ValuationSummary,
    ReportTemplate,
    Report
)


def format_currency(value: float, currency: str = "CAD") -> str:
    """Format a number as currency"""
    if currency == "CAD":
        return f"${value:,.0f} CAD"
    return f"{currency} {value:,.0f}"


def generate_quick_report_markdown(db: Session, project_id: UUID) -> str:
    """
    Generate a Quick Valuation Summary report in Markdown format

    Args:
        db: Database session
        project_id: UUID of the project

    Returns:
        str: Report ID

    Raises:
        ValueError: If required data is missing
    """
    # Load all required data
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError(f"Project not found: {project_id}")

    client = db.query(Client).filter(Client.id == project.client_id).first()
    if not client:
        raise ValueError(f"Client not found: {project.client_id}")

    financial_input = db.query(FinancialInput).filter(
        FinancialInput.project_id == project_id
    ).first()

    valuation_summary = db.query(ValuationSummary).filter(
        ValuationSummary.project_id == project_id
    ).first()

    if not valuation_summary:
        raise ValueError(f"No valuation summary found for project: {project_id}")

    # Get report template
    template = db.query(ReportTemplate).filter(
        ReportTemplate.code == 'QUICK_SUMMARY',
        ReportTemplate.is_active == True
    ).first()

    if not template:
        raise ValueError("Quick Summary report template not found")

    # Determine metric used
    metric_info = ""
    if financial_input:
        if financial_input.sde:
            metric_info = f"**SDE (Seller's Discretionary Earnings):** {format_currency(float(financial_input.sde))}\n"
        if financial_input.ebitda:
            metric_info += f"**EBITDA:** {format_currency(float(financial_input.ebitda))}\n"
        if financial_input.revenue:
            metric_info += f"**Annual Revenue:** {format_currency(float(financial_input.revenue))}\n"

    # Build Markdown content
    markdown_content = f"""# Quick Valuation Summary – {project.business_name}

**Prepared for:** {client.name}
**Date:** {datetime.now().strftime('%B %d, %Y')}
**Location:** {project.location or 'Not specified'}
**Industry Code (NAICS):** {project.industry_code}

---

## Business Overview

{metric_info}

---

## Estimated Value Range (Quick Multiple Method)

| Scenario | Estimated Value |
|----------|----------------|
| **Low**  | {format_currency(float(valuation_summary.recommended_value_low), valuation_summary.currency)} |
| **Mid**  | {format_currency(float(valuation_summary.recommended_value_mid), valuation_summary.currency)} |
| **High** | {format_currency(float(valuation_summary.recommended_value_high), valuation_summary.currency)} |

---

## Important Notes

This Quick Valuation Summary provides a **preliminary estimate** of business value based on industry multiples and financial metrics provided.

**Key Considerations:**

- This valuation is intended for **planning and discussion purposes only**
- The estimate is based on industry-standard multiples for comparable businesses
- Actual transaction value may vary based on:
  - Detailed due diligence findings
  - Market conditions at time of sale
  - Business-specific factors (customer concentration, growth trends, etc.)
  - Asset condition and transferability
  - Financing terms and structure

**Next Steps:**

For a more comprehensive valuation, consider:
- Standard Valuation (includes adjusted multiples and comparables analysis)
- Full Valuation Report (detailed DCF, market approach, and asset-based methods)

---

**Prepared by Capital Link Exit Builder**
*Professional Business Valuation Services*

---

*This report is confidential and prepared exclusively for {client.name}. It should not be distributed or relied upon by third parties without written consent from Capital Link.*
"""

    # Create report record
    report = Report(
        project_id=project_id,
        report_template_id=template.id,
        title=f"Quick Valuation Summary – {project.business_name}",
        language='en',
        status='draft',
        content_markdown=markdown_content
    )
    db.add(report)

    # Update project status
    project.status = 'reported'

    db.commit()
    db.refresh(report)

    return str(report.id)


def get_report_content(db: Session, report_id: UUID) -> Optional[str]:
    """
    Get the markdown content of a report

    Args:
        db: Database session
        report_id: UUID of the report

    Returns:
        str: Markdown content or None if not found
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if report:
        return report.content_markdown
    return None


def get_project_reports(db: Session, project_id: UUID) -> list[Report]:
    """
    Get all reports for a project

    Args:
        db: Database session
        project_id: UUID of the project

    Returns:
        list[Report]: List of reports
    """
    return db.query(Report).filter(Report.project_id == project_id).all()
