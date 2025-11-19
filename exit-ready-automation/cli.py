"""
CLI for Exit Ready Automation using Typer.
"""
import asyncio
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.core.workflow import CaseStatus
from app.schemas.case import CaseCreate
from app.services import (
    CaseService,
    IntakeService,
    DocsService,
    ValuationService,
    DraftsService,
    ExportService,
    DeliveryService,
)

app = typer.Typer(
    name="exit-ready",
    help="Exit Ready Automation CLI - Manage Exit Ready cases",
    add_completion=False,
)
console = Console()


# ==================== Helper Functions ====================

async def get_session() -> AsyncSession:
    """Get async database session."""
    async with AsyncSessionLocal() as session:
        return session


def run_async(coro):
    """Run async function in sync context."""
    return asyncio.run(coro)


# ==================== Case Management Commands ====================

@app.command()
def create_case(
    owner_name: str = typer.Option(..., prompt=True),
    owner_email: str = typer.Option(..., prompt=True),
    company_name: str = typer.Option(..., prompt=True),
    industry: Optional[str] = typer.Option(None),
    region: Optional[str] = typer.Option(None),
):
    """Create a new Exit Ready case."""

    async def _create():
        session = await get_session()
        service = CaseService(session)

        case_data = CaseCreate(
            owner_name=owner_name,
            owner_email=owner_email,
            company_name=company_name,
            industry=industry,
            region=region,
        )

        case = await service.create_case(case_data, actor="cli")
        await session.commit()

        console.print(f"✅ Created case: [bold]{case.case_code}[/bold]")
        console.print(f"   ID: {case.id}")
        console.print(f"   Company: {case.company_name}")
        console.print(f"   Status: {case.status}")

    run_async(_create())


@app.command()
def list_cases(
    status: Optional[str] = typer.Option(None, help="Filter by status"),
    limit: int = typer.Option(50, help="Max cases to show"),
):
    """List all Exit Ready cases."""

    async def _list():
        session = await get_session()
        service = CaseService(session)

        cases, total = await service.list_cases(status=status, page=1, page_size=limit)

        table = Table(title=f"Exit Ready Cases (Total: {total})")
        table.add_column("ID", style="cyan")
        table.add_column("Case Code", style="magenta")
        table.add_column("Company", style="green")
        table.add_column("Owner", style="yellow")
        table.add_column("Status", style="blue")
        table.add_column("Created", style="white")

        for case in cases:
            table.add_row(
                str(case.id),
                case.case_code,
                case.company_name,
                case.owner_name,
                case.status,
                case.created_at.strftime("%Y-%m-%d"),
            )

        console.print(table)

    run_async(_list())


@app.command()
def get_case(
    case_id: int = typer.Argument(..., help="Case ID"),
):
    """Get details of a specific case."""

    async def _get():
        session = await get_session()
        service = CaseService(session)

        case = await service.get_case(case_id)

        if not case:
            console.print(f"❌ Case {case_id} not found")
            raise typer.Exit(1)

        console.print(f"\n[bold]Case: {case.case_code}[/bold]")
        console.print(f"  ID: {case.id}")
        console.print(f"  Company: {case.company_name}")
        console.print(f"  Owner: {case.owner_name} ({case.owner_email})")
        console.print(f"  Industry: {case.industry or 'N/A'}")
        console.print(f"  Status: [bold]{case.status}[/bold]")
        console.print(f"  Created: {case.created_at}")
        console.print(f"  Updated: {case.updated_at}")

        if case.intake_sent_at:
            console.print(f"  Intake Sent: {case.intake_sent_at}")
        if case.valuation_last_run_at:
            console.print(f"  Valuation Run: {case.valuation_last_run_at}")
        if case.report_url:
            console.print(f"  Report: {case.report_url}")

    run_async(_get())


# ==================== Workflow Commands ====================

@app.command()
def send_intake(
    case_id: int = typer.Argument(..., help="Case ID"),
):
    """Send intake form link to seller."""

    async def _send():
        session = await get_session()
        service = IntakeService(session)

        try:
            result = await service.send_intake_link(case_id, actor="cli")
            await session.commit()
            console.print(f"✅ Intake link sent for case {case_id}")
            console.print(f"   Result: {result.get('status', 'unknown')}")
        except ValueError as e:
            console.print(f"❌ Error: {str(e)}")
            raise typer.Exit(1)

    run_async(_send())


@app.command()
def generate_checklist(
    case_id: int = typer.Argument(..., help="Case ID"),
):
    """Generate document checklist for a case."""

    async def _generate():
        session = await get_session()
        service = DocsService(session)

        try:
            checklist = await service.generate_checklist(case_id, actor="cli")
            await session.commit()

            console.print(f"✅ Generated checklist for case {case_id}")
            console.print(f"   Total documents: {checklist.total_docs}")
            console.print(f"   Required: {checklist.required_docs}")
            console.print(f"   Pending: {checklist.pending_docs}")
        except ValueError as e:
            console.print(f"❌ Error: {str(e)}")
            raise typer.Exit(1)

    run_async(_generate())


@app.command()
def run_valuation(
    case_id: int = typer.Argument(..., help="Case ID"),
):
    """Run valuation for a case."""

    async def _run():
        session = await get_session()
        service = ValuationService(session)

        try:
            console.print(f"⏳ Running valuation for case {case_id}...")
            result = await service.run_valuation(case_id, actor="cli")
            await session.commit()

            console.print(f"✅ Valuation complete")
            console.print(f"   Range: ${result.valuation_range.low:,.0f} - ${result.valuation_range.high:,.0f}")
            console.print(f"   Mid: ${result.valuation_range.mid:,.0f}")
            console.print(f"   Methodology: {result.methodology}")
        except ValueError as e:
            console.print(f"❌ Error: {str(e)}")
            raise typer.Exit(1)

    run_async(_run())


@app.command()
def generate_drafts(
    case_id: int = typer.Argument(..., help="Case ID"),
):
    """Generate document drafts (teaser, summary, CIM)."""

    async def _generate():
        session = await get_session()
        service = DraftsService(session)

        try:
            console.print(f"⏳ Generating drafts for case {case_id}...")
            drafts = await service.generate_drafts(case_id, actor="cli")
            await session.commit()

            console.print(f"✅ Drafts generated")
            console.print(f"   Sections: {', '.join(drafts.keys())}")
        except ValueError as e:
            console.print(f"❌ Error: {str(e)}")
            raise typer.Exit(1)

    run_async(_generate())


@app.command()
def export_report(
    case_id: int = typer.Argument(..., help="Case ID"),
):
    """Export Exit Ready report to PDF."""

    async def _export():
        session = await get_session()
        service = ExportService(session)

        try:
            console.print(f"⏳ Exporting report for case {case_id}...")
            report_url = await service.export_exit_ready_report(case_id, actor="cli")
            await session.commit()

            console.print(f"✅ Report exported")
            console.print(f"   URL: {report_url}")
        except ValueError as e:
            console.print(f"❌ Error: {str(e)}")
            raise typer.Exit(1)

    run_async(_export())


@app.command()
def deliver_report(
    case_id: int = typer.Argument(..., help="Case ID"),
    channel: str = typer.Option("email", help="Delivery channel"),
):
    """Deliver Exit Ready report to seller."""

    async def _deliver():
        session = await get_session()
        service = DeliveryService(session)

        try:
            console.print(f"⏳ Delivering report for case {case_id}...")
            result = await service.deliver_report(case_id, channel=channel, actor="cli")
            await session.commit()

            console.print(f"✅ Report delivered via {channel}")
        except ValueError as e:
            console.print(f"❌ Error: {str(e)}")
            raise typer.Exit(1)

    run_async(_deliver())


@app.command()
def close_case(
    case_id: int = typer.Argument(..., help="Case ID"),
    next_step: str = typer.Option("none", help="Next step"),
    notes: Optional[str] = typer.Option(None, help="Closing notes"),
):
    """Close an Exit Ready case."""

    async def _close():
        session = await get_session()
        service = DeliveryService(session)

        try:
            result = await service.close_case(
                case_id,
                next_step=next_step,
                notes=notes,
                actor="cli"
            )
            await session.commit()

            console.print(f"✅ Case closed: {result['case_code']}")
            console.print(f"   Next step: {next_step}")
        except ValueError as e:
            console.print(f"❌ Error: {str(e)}")
            raise typer.Exit(1)

    run_async(_close())


# ==================== Utility Commands ====================

@app.command()
def stats():
    """Show case statistics."""

    async def _stats():
        session = await get_session()
        service = CaseService(session)

        stats = await service.get_stats()

        console.print("\n[bold]Exit Ready Statistics[/bold]")
        console.print(f"  Total Cases: {stats['total_cases']}")
        console.print("\n  By Status:")
        for status, count in stats['by_status'].items():
            console.print(f"    {status}: {count}")

    run_async(_stats())


@app.command()
def version():
    """Show version information."""
    console.print(f"\n[bold]{settings.app_name}[/bold]")
    console.print(f"  Version: {settings.app_version}")
    console.print(f"  Environment: {settings.environment}")


if __name__ == "__main__":
    app()
