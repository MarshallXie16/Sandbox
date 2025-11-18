"""
CLI commands for worker operations.
"""
import typer
import time
from rich.console import Console
from rich.live import Live
from rich.table import Table

from app.core.database import init_db
from app.scheduler import EmailWorker

console = Console()
app = typer.Typer(help="Worker commands")


@app.command("run")
def run_worker(
    continuous: bool = typer.Option(False, "--continuous", "-c", help="Run continuously"),
    interval: int = typer.Option(60, "--interval", "-i", help="Interval between runs (seconds)"),
    max_sends: int = typer.Option(100, "--max-sends", "-m", help="Max emails per run"),
):
    """
    Run the email sending worker.
    """
    try:
        init_db()

        console.print("[bold cyan]Email Campaign Worker[/bold cyan]")
        console.print(f"Max sends per run: {max_sends}")

        if continuous:
            console.print(f"Running continuously (interval: {interval}s)")
            console.print("Press Ctrl+C to stop\n")

            run_count = 0
            try:
                while True:
                    run_count += 1
                    console.print(f"[bold]Run #{run_count}[/bold]")

                    worker = EmailWorker()
                    stats = worker.run_once(max_sends_per_run=max_sends)

                    # Display stats
                    _display_stats(stats)

                    if not continuous:
                        break

                    console.print(f"\nWaiting {interval} seconds before next run...")
                    time.sleep(interval)

            except KeyboardInterrupt:
                console.print("\n[yellow]Worker stopped by user[/yellow]")
                return

        else:
            worker = EmailWorker()
            stats = worker.run_once(max_sends_per_run=max_sends)
            _display_stats(stats)

        console.print("\n[green]✓ Worker completed[/green]")

    except Exception as e:
        console.print(f"[red]Error running worker: {e}[/red]")
        raise typer.Exit(1)


def _display_stats(stats: dict):
    """Display worker run statistics."""
    table = Table(title="Worker Run Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Campaigns Processed", str(stats["campaigns_processed"]))
    table.add_row("Emails Sent", str(stats["emails_sent"]))
    table.add_row("Emails Failed", str(stats["emails_failed"]))
    table.add_row("Campaigns Completed", str(stats["campaigns_completed"]))

    if "end_time" in stats:
        duration = (stats["end_time"] - stats["start_time"]).total_seconds()
        table.add_row("Duration", f"{duration:.2f}s")

    console.print(table)


@app.command("status")
def worker_status():
    """
    Show current worker status and campaign queue.
    """
    try:
        init_db()

        from app.core.database import get_db
        from app.repositories import CampaignRepository, RecipientRepository
        from app.models import CampaignStatus, RecipientStatus

        with get_db() as db:
            campaign_repo = CampaignRepository(db)
            recipient_repo = RecipientRepository(db)

            # Get active campaigns
            active_campaigns = campaign_repo.get_active_campaigns()

            if not active_campaigns:
                console.print("[yellow]No active campaigns[/yellow]")
                return

            table = Table(title="Active Campaigns")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Status")
            table.add_column("Pending")
            table.add_column("Sent")
            table.add_column("Failed")

            for campaign in active_campaigns:
                pending = recipient_repo.count_by_campaign_and_status(
                    campaign.id, RecipientStatus.PENDING
                )
                sent = recipient_repo.count_by_campaign_and_status(
                    campaign.id, RecipientStatus.SENT
                )
                failed = recipient_repo.count_by_campaign_and_status(
                    campaign.id, RecipientStatus.FAILED
                )

                table.add_row(
                    str(campaign.id),
                    campaign.name,
                    campaign.status.value,
                    str(pending),
                    str(sent),
                    str(failed)
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error getting worker status: {e}[/red]")
        raise typer.Exit(1)
