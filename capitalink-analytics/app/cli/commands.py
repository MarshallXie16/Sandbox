"""CLI command implementations."""

import asyncio
from datetime import date, datetime
from typing import Optional

from rich.console import Console
from rich.table import Table

from app.core.database import db_manager
from app.repositories.analytics import AnalyticsRepository
from app.repositories.crm_read import CrmReadRepository
from app.repositories.exit_ready_read import ExitReadyReadRepository
from app.repositories.facilitator_read import FacilitatorReadRepository
from app.services.crm_analytics import CrmAnalyticsService
from app.services.exit_ready_analytics import ExitReadyAnalyticsService
from app.services.facilitator_analytics import FacilitatorAnalyticsService

console = Console()


async def run_snapshot(snapshot_date: str, domain: Optional[str] = None):
    """
    Run analytics snapshot for a specific date.

    Args:
        snapshot_date: Date in YYYY-MM-DD format
        domain: Specific domain to snapshot (optional)
    """
    await db_manager.initialize()

    try:
        # Parse date
        snapshot_dt = datetime.strptime(snapshot_date, "%Y-%m-%d").date()

        console.print(f"[bold blue]Running analytics snapshot for {snapshot_dt}[/bold blue]")

        # Determine which domains to snapshot
        domains_to_process = [domain] if domain else ["exit_ready", "facilitator", "crm"]

        async with await db_manager.get_analytics_session() as session:
            analytics_repo = AnalyticsRepository(session)

            for dom in domains_to_process:
                console.print(f"\n[yellow]Processing domain: {dom}[/yellow]")

                # Create job record
                job = await analytics_repo.create_job(
                    job_type="snapshot",
                    domain=dom,
                    metadata={"snapshot_date": snapshot_date},
                )

                try:
                    data = {}

                    if dom == "exit_ready":
                        repo = ExitReadyReadRepository(db_manager.exit_ready_engine)
                        service = ExitReadyAnalyticsService(repo)
                        pipeline = await service.get_pipeline_summary()
                        data = {
                            "total_cases": pipeline.total_cases,
                            "by_status": pipeline.by_status,
                        }

                    elif dom == "facilitator":
                        repo = FacilitatorReadRepository(db_manager.facilitator_engine)
                        service = FacilitatorAnalyticsService(repo)
                        engagements = await service.get_engagement_status_summary()
                        revenue = await service.get_revenue_summary()
                        data = {
                            "total_engagements": engagements.total_engagements,
                            "by_status": engagements.by_status,
                            "revenue": {
                                "total_offer_fees": revenue.total_offer_fees,
                                "total_success_fee_net": revenue.total_success_fee_net,
                                "total_revenue": revenue.total_revenue,
                                "closed_success_count": revenue.closed_success_count,
                            },
                        }

                    elif dom == "crm":
                        repo = CrmReadRepository(db_manager.crm_engine)
                        service = CrmAnalyticsService(repo)
                        overview = await service.get_basic_counts()
                        data = {
                            "total_contacts": overview.total_contacts,
                            "total_sellers": overview.total_sellers,
                            "total_buyers": overview.total_buyers,
                            "total_companies": overview.total_companies,
                            "total_listings": overview.total_listings,
                            "active_listings": overview.active_listings,
                        }

                    # Save snapshot
                    await analytics_repo.create_snapshot(
                        snapshot_date=snapshot_dt,
                        domain=dom,
                        data=data,
                    )

                    # Complete job
                    await analytics_repo.complete_job(job.id)
                    console.print(f"[green]✓ Snapshot saved for {dom}[/green]")

                except Exception as e:
                    # Mark job as failed
                    await analytics_repo.complete_job(job.id, error_message=str(e))
                    console.print(f"[red]✗ Error processing {dom}: {e}[/red]")

        console.print("\n[bold green]Snapshot complete![/bold green]")

    finally:
        await db_manager.close()


async def exit_ready_summary():
    """Display Exit Ready summary statistics."""
    await db_manager.initialize()

    try:
        repo = ExitReadyReadRepository(db_manager.exit_ready_engine)
        service = ExitReadyAnalyticsService(repo)

        console.print("\n[bold blue]Exit Ready Analytics Summary[/bold blue]\n")

        # Pipeline
        pipeline = await service.get_pipeline_summary()

        table = Table(title="Pipeline Status")
        table.add_column("Status", style="cyan")
        table.add_column("Count", justify="right", style="magenta")
        table.add_column("Percentage", justify="right", style="green")

        for status, count in pipeline.by_status.items():
            percentage = (count / pipeline.total_cases * 100) if pipeline.total_cases > 0 else 0
            table.add_row(
                status.replace("_", " ").title(),
                str(count),
                f"{percentage:.1f}%",
            )

        table.add_row("", "", "", style="dim")
        table.add_row("[bold]Total[/bold]", f"[bold]{pipeline.total_cases}[/bold]", "[bold]100.0%[/bold]")

        console.print(table)

        # Durations
        console.print("\n[bold]Stage Durations[/bold]\n")
        durations = await service.get_stage_durations()

        duration_table = Table(title="Average Duration by Stage")
        duration_table.add_column("Stage", style="cyan")
        duration_table.add_column("Avg Days", justify="right", style="magenta")
        duration_table.add_column("Median Days", justify="right", style="yellow")
        duration_table.add_column("Sample Size", justify="right", style="green")

        for dur in durations.durations:
            avg_str = f"{dur.average_days:.1f}" if dur.average_days else "N/A"
            median_str = f"{dur.median_days:.0f}" if dur.median_days else "N/A"

            duration_table.add_row(
                dur.stage.replace("_", " ").title(),
                avg_str,
                median_str,
                str(dur.sample_size),
            )

        console.print(duration_table)
        console.print()

    finally:
        await db_manager.close()


async def facilitator_revenue(from_date: Optional[str] = None, to_date: Optional[str] = None):
    """Display Facilitator revenue summary."""
    await db_manager.initialize()

    try:
        repo = FacilitatorReadRepository(db_manager.facilitator_engine)
        service = FacilitatorAnalyticsService(repo)

        # Parse dates
        from_dt = datetime.fromisoformat(from_date) if from_date else None
        to_dt = datetime.fromisoformat(to_date) if to_date else None

        period_str = ""
        if from_dt or to_dt:
            period_str = f" ({from_date or 'start'} to {to_date or 'now'})"

        console.print(f"\n[bold blue]Facilitator Revenue Summary{period_str}[/bold blue]\n")

        revenue = await service.get_revenue_summary(from_date=from_dt, to_date=to_dt)

        table = Table(title="Revenue Breakdown")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="magenta")

        table.add_row("Offer Fees", f"${revenue.total_offer_fees:,.2f}")
        table.add_row("Success Fee (Gross)", f"${revenue.total_success_fee_gross:,.2f}")
        table.add_row("Success Fee (Net)", f"${revenue.total_success_fee_net:,.2f}")
        table.add_row("", "", style="dim")
        table.add_row("[bold]Total Revenue[/bold]", f"[bold]${revenue.total_revenue:,.2f}[/bold]")
        table.add_row("", "", style="dim")
        table.add_row("Successful Closings", str(revenue.closed_success_count))

        console.print(table)
        console.print()

    finally:
        await db_manager.close()


async def facilitator_funnel():
    """Display Facilitator buyer introduction funnel."""
    await db_manager.initialize()

    try:
        repo = FacilitatorReadRepository(db_manager.facilitator_engine)
        service = FacilitatorAnalyticsService(repo)

        console.print("\n[bold blue]Facilitator Buyer Introduction Funnel[/bold blue]\n")

        funnel = await service.get_buyer_intro_funnel()

        table = Table(title="Buyer Progression")
        table.add_column("Stage", style="cyan")
        table.add_column("Count", justify="right", style="magenta")
        table.add_column("Conversion Rate", justify="right", style="green")

        for stage in funnel.funnel_stages:
            conv_str = (
                f"{stage.conversion_rate:.1f}%" if stage.conversion_rate is not None else "-"
            )
            table.add_row(
                stage.stage.replace("_", " ").title(),
                str(stage.count),
                conv_str,
            )

        console.print(table)
        console.print()

    finally:
        await db_manager.close()


async def crm_overview():
    """Display CRM overview statistics."""
    await db_manager.initialize()

    try:
        repo = CrmReadRepository(db_manager.crm_engine)
        service = CrmAnalyticsService(repo)

        console.print("\n[bold blue]CRM Overview[/bold blue]\n")

        overview = await service.get_basic_counts()

        table = Table(title="CRM Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="magenta")

        table.add_row("Total Contacts", str(overview.total_contacts))
        table.add_row("  - Sellers", str(overview.total_sellers))
        table.add_row("  - Buyers", str(overview.total_buyers))
        table.add_row("", "", style="dim")
        table.add_row("Total Companies", str(overview.total_companies))
        table.add_row("", "", style="dim")
        table.add_row("Total Listings", str(overview.total_listings))
        table.add_row("Active Listings", str(overview.active_listings))

        console.print(table)
        console.print()

    finally:
        await db_manager.close()
