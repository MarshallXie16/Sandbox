"""
CLI interface for HubSpot-IndieStack sync service.

Provides commands for manual sync operations, configuration viewing,
and troubleshooting.
"""

import json
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from app.core.config import settings
from app.core.database import init_db, get_db_context
from app.core.logging import configure_logging, get_logger
from app.mappings.engine import MappingEngine
from app.models.tracking import EntityType, SyncDirection, SyncRun, SyncError
from app.services.sync_service import SyncService

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Create Typer app
app = typer.Typer(
    name="indie-hubspot-sync",
    help="HubSpot ↔ IndieStack synchronization CLI",
    add_completion=False,
)

console = Console()


# Helper functions

def parse_direction(direction_str: str) -> SyncDirection:
    """Parse direction string to enum."""
    direction_map = {
        "indie_to_hubspot": SyncDirection.INDIE_TO_HUBSPOT,
        "hubspot_to_indie": SyncDirection.HUBSPOT_TO_INDIE,
        "bidirectional": SyncDirection.BIDIRECTIONAL,
    }
    return direction_map.get(direction_str.lower(), SyncDirection.BIDIRECTIONAL)


def print_sync_results(results: dict, dry_run: bool = False):
    """Pretty print sync results."""
    table = Table(title="Sync Results" + (" (DRY RUN)" if dry_run else ""))

    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Count", style="magenta", justify="right")

    table.add_row("Created", str(results.get("created", 0)))
    table.add_row("Updated", str(results.get("updated", 0)))
    table.add_row("Skipped", str(results.get("skipped", 0)))
    table.add_row("Errors", str(results.get("errors", 0)))

    console.print(table)


# Commands

@app.command()
def sync_contacts(
    direction: str = typer.Option(
        "bidirectional",
        "--direction",
        "-d",
        help="Sync direction: indie_to_hubspot, hubspot_to_indie, bidirectional",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Simulate sync without making changes",
    ),
):
    """Synchronize contacts between IndieStack and HubSpot."""
    console.print(f"[bold]Syncing contacts ({direction})...[/bold]")

    init_db()
    sync_service = SyncService()
    direction_enum = parse_direction(direction)

    results = sync_service.sync_contacts(direction=direction_enum, dry_run=dry_run)
    print_sync_results(results, dry_run)


@app.command()
def sync_companies(
    direction: str = typer.Option(
        "bidirectional",
        "--direction",
        "-d",
        help="Sync direction",
    ),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Synchronize companies between IndieStack and HubSpot."""
    console.print(f"[bold]Syncing companies ({direction})...[/bold]")

    init_db()
    sync_service = SyncService()
    direction_enum = parse_direction(direction)

    results = sync_service.sync_companies(direction=direction_enum, dry_run=dry_run)
    print_sync_results(results, dry_run)


@app.command()
def sync_deals(
    direction: str = typer.Option(
        "bidirectional",
        "--direction",
        "-d",
        help="Sync direction",
    ),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Synchronize deals between IndieStack and HubSpot."""
    console.print(f"[bold]Syncing deals ({direction})...[/bold]")

    init_db()
    sync_service = SyncService()
    direction_enum = parse_direction(direction)

    results = sync_service.sync_deals(direction=direction_enum, dry_run=dry_run)
    print_sync_results(results, dry_run)


@app.command()
def sync_all(
    direction: str = typer.Option(
        "bidirectional",
        "--direction",
        "-d",
        help="Sync direction",
    ),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Synchronize all entity types (contacts, companies, deals)."""
    console.print(f"[bold]Syncing all entities ({direction})...[/bold]")

    init_db()
    sync_service = SyncService()
    direction_enum = parse_direction(direction)

    results = sync_service.sync_all(direction=direction_enum, dry_run=dry_run)

    # Print individual results
    for entity_type, entity_results in results.get("results", {}).items():
        console.print(f"\n[bold cyan]{entity_type.capitalize()}:[/bold cyan]")
        print_sync_results(entity_results, dry_run)

    # Print totals
    console.print("\n[bold]Totals:[/bold]")
    print_sync_results(results.get("totals", {}), dry_run)


@app.command()
def show_mappings(
    entity: Optional[str] = typer.Argument(
        None,
        help="Entity type to show mappings for (contacts, companies, deals). Shows all if not specified.",
    ),
):
    """Display field mapping configuration."""
    mapper = MappingEngine()

    if entity:
        # Show specific entity
        entity_type = EntityType(entity.rstrip('s'))  # Remove trailing 's'
        mappings = mapper.get_entity_mappings(entity_type)

        table = Table(title=f"{entity.capitalize()} Field Mappings")
        table.add_column("IndieStack Field", style="cyan")
        table.add_column("HubSpot Property", style="magenta")
        table.add_column("Direction", style="green")
        table.add_column("Transform", style="yellow")

        for field_name, config in mappings.items():
            table.add_row(
                config["indie_field"],
                config["hubspot_property"],
                config["direction"],
                config.get("transform", "-"),
            )

        console.print(table)
    else:
        # Show all entities
        for entity_type in [EntityType.CONTACT, EntityType.COMPANY, EntityType.DEAL]:
            entity_name = f"{entity_type.value}s"
            mappings = mapper.get_entity_mappings(entity_type)

            console.print(f"\n[bold cyan]{entity_name.capitalize()}:[/bold cyan]")
            console.print(f"  Total fields: {len(mappings)}")

            bidirectional = sum(
                1 for c in mappings.values() if c.get("direction") == "bidirectional"
            )
            indie_to_hs = sum(
                1 for c in mappings.values() if c.get("direction") == "indie_to_hubspot"
            )
            hs_to_indie = sum(
                1 for c in mappings.values() if c.get("direction") == "hubspot_to_indie"
            )

            console.print(f"  Bidirectional: {bidirectional}")
            console.print(f"  IndieStack → HubSpot: {indie_to_hs}")
            console.print(f"  HubSpot → IndieStack: {hs_to_indie}")


@app.command()
def list_runs(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of runs to show"),
):
    """List recent sync runs."""
    init_db()

    with get_db_context() as db:
        runs = db.query(SyncRun).order_by(SyncRun.started_at.desc()).limit(limit).all()

        table = Table(title="Recent Sync Runs")
        table.add_column("ID", style="cyan")
        table.add_column("Started", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Direction", style="yellow")
        table.add_column("Duration", style="blue")

        for run in runs:
            duration = "-"
            if run.finished_at:
                delta = run.finished_at - run.started_at
                duration = f"{delta.total_seconds():.1f}s"

            table.add_row(
                str(run.id),
                run.started_at.strftime("%Y-%m-%d %H:%M:%S"),
                run.status.value,
                run.direction.value,
                duration,
            )

        console.print(table)


@app.command()
def show_run(
    run_id: int = typer.Argument(..., help="Sync run ID to display"),
):
    """Show detailed information about a sync run."""
    init_db()

    with get_db_context() as db:
        run = db.query(SyncRun).filter(SyncRun.id == run_id).first()

        if not run:
            console.print(f"[red]Sync run {run_id} not found[/red]")
            raise typer.Exit(1)

        # Run details
        console.print(f"\n[bold]Sync Run #{run.id}[/bold]")
        console.print(f"Status: {run.status.value}")
        console.print(f"Direction: {run.direction.value}")
        console.print(f"Started: {run.started_at}")
        console.print(f"Finished: {run.finished_at or 'In progress'}")

        if run.summary:
            console.print(f"\n[bold]Summary:[/bold]")
            summary = json.loads(run.summary)
            print_sync_results(summary)

        # Errors
        errors = db.query(SyncError).filter(SyncError.sync_run_id == run_id).all()

        if errors:
            console.print(f"\n[bold red]Errors ({len(errors)}):[/bold red]")
            for error in errors[:10]:  # Show first 10 errors
                console.print(f"\n  Entity: {error.entity_type.value}")
                console.print(f"  IndieStack ID: {error.indie_id or 'N/A'}")
                console.print(f"  HubSpot ID: {error.hubspot_id or 'N/A'}")
                console.print(f"  Error: {error.error_message}")

            if len(errors) > 10:
                console.print(f"\n  ... and {len(errors) - 10} more errors")


@app.command()
def init():
    """Initialize the sync tracking database."""
    console.print("[bold]Initializing sync tracking database...[/bold]")
    init_db()
    console.print("[green]✓ Database initialized successfully[/green]")


@app.command()
def config():
    """Display current configuration."""
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")

    # Mask sensitive values
    hubspot_token = settings.hubspot_private_app_token
    masked_token = f"{hubspot_token[:10]}..." if len(hubspot_token) > 10 else "***"

    table.add_row("HubSpot Token", masked_token)
    table.add_row("IndieStack Integration Mode", settings.indie_integration_mode)
    table.add_row("IndieStack DB Host", settings.indie_db_host)
    table.add_row("IndieStack DB Name", settings.indie_db_name)
    table.add_row("Sync DB URL", settings.sync_db_url)
    table.add_row("Default Sync Direction", settings.default_sync_direction.value)
    table.add_row("Conflict Resolution", settings.sync_conflict_resolution)
    table.add_row("Batch Size", str(settings.sync_batch_size))
    table.add_row("Log Level", settings.log_level)

    console.print(table)


if __name__ == "__main__":
    app()
