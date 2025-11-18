"""CLI tools for the engagement tracker."""
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from app.core import get_session, init_db, logger, settings
from app.models import EntityType, ScoringProfile
from app.repositories import ScoringProfileRepository, EngagementRepository
from app.scoring import get_scoring_engine
from app.sources import SourceManager

app = typer.Typer(help="Indie Engagement Tracker CLI")
console = Console()


@app.command()
def init() -> None:
    """Initialize the database (create all tables)."""
    console.print("[bold blue]Initializing database...[/bold blue]")

    try:
        init_db()
        console.print("[bold green]✓ Database initialized successfully![/bold green]")

        # Create default scoring profile if it doesn't exist
        db = get_session()
        try:
            repo = ScoringProfileRepository(db)
            default = repo.get_default()

            if not default:
                console.print("[bold yellow]Creating default scoring profile...[/bold yellow]")

                default_rules = {
                    "event_weights": {
                        "email_sent": 1.0,
                        "email_open": 3.0,
                        "email_click": 5.0,
                        "email_reply": 10.0,
                        "email_bounce": -2.0,
                        "call": 8.0,
                        "meeting": 15.0,
                        "message": 5.0,
                        "note_added": 3.0,
                        "task_completed": 5.0,
                        "deal_created": 20.0,
                        "deal_stage_change": 15.0,
                        "deal_won": 50.0,
                        "deal_lost": -10.0,
                        "form_submit": 12.0,
                        "page_view": 1.0,
                        "download": 7.0,
                    },
                    "time_decay": {
                        "enabled": True,
                        "decay_days": 90,
                        "decay_factor": 0.5,
                    },
                }

                repo.create(
                    name="Default",
                    description="Default scoring profile with standard event weights and 90-day decay",
                    rules=default_rules,
                    is_default=True,
                )

                console.print("[bold green]✓ Default scoring profile created![/bold green]")
            else:
                console.print(
                    f"[dim]Default scoring profile already exists: {default.name}[/dim]"
                )

        finally:
            db.close()

    except Exception as e:
        console.print(f"[bold red]✗ Error: {str(e)}[/bold red]")
        raise typer.Exit(code=1)


@app.command()
def ingest_all(
    since: Optional[str] = typer.Option(
        None, help="Only ingest events after this datetime (ISO format)"
    ),
    limit: Optional[int] = typer.Option(None, help="Maximum events per source"),
    dry_run: bool = typer.Option(False, help="Don't save to database, just show what would be done"),
) -> None:
    """Ingest events from all configured sources."""
    console.print("[bold blue]Starting event ingestion...[/bold blue]")

    if dry_run:
        console.print("[bold yellow]DRY RUN MODE - No changes will be saved[/bold yellow]")

    # Parse since datetime if provided
    since_dt = None
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            console.print(f"[dim]Fetching events since: {since_dt}[/dim]")
        except ValueError:
            console.print("[bold red]✗ Invalid datetime format. Use ISO format (e.g., 2024-01-01T00:00:00)[/bold red]")
            raise typer.Exit(code=1)

    db = get_session()
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Ingesting events...", total=None)

            manager = SourceManager(db)
            stats = manager.ingest_from_all_sources(since=since_dt, limit=limit, dry_run=dry_run)

            progress.update(task, completed=True)

        # Display results
        console.print("\n[bold green]✓ Ingestion complete![/bold green]\n")

        table = Table(title="Ingestion Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="magenta", justify="right")

        table.add_row("Total Fetched", str(stats["total_fetched"]))
        table.add_row("New Events", str(stats["total_new"]))
        table.add_row("Duplicates", str(stats["total_duplicates"]))
        table.add_row("Errors", str(stats["total_errors"]))

        console.print(table)

        # Show per-source stats
        if stats["sources"]:
            console.print("\n[bold]Per-Source Statistics:[/bold]\n")

            source_table = Table()
            source_table.add_column("Source", style="cyan")
            source_table.add_column("Fetched", justify="right")
            source_table.add_column("New", justify="right", style="green")
            source_table.add_column("Duplicates", justify="right", style="yellow")
            source_table.add_column("Errors", justify="right", style="red")

            for source_name, source_stats in stats["sources"].items():
                source_table.add_row(
                    source_name,
                    str(source_stats["fetched"]),
                    str(source_stats["new"]),
                    str(source_stats["duplicates"]),
                    str(source_stats["errors"]),
                )

            console.print(source_table)

    except Exception as e:
        console.print(f"[bold red]✗ Error: {str(e)}[/bold red]")
        logger.exception("Ingestion failed")
        raise typer.Exit(code=1)
    finally:
        db.close()


@app.command()
def recalc_all(
    profile_id: Optional[int] = typer.Option(None, help="Scoring profile ID to use"),
    entity_type: Optional[str] = typer.Option(None, help="Entity type filter (contact/company/deal)"),
    min_events: int = typer.Option(0, help="Minimum events required"),
) -> None:
    """Recalculate engagement scores for all entities."""
    console.print("[bold blue]Starting score recalculation...[/bold blue]")

    db = get_session()
    try:
        # Get scoring engine
        try:
            engine = get_scoring_engine(db, profile_id)
            console.print(f"[dim]Using scoring profile: {engine.profile.name}[/dim]")
        except ValueError as e:
            console.print(f"[bold red]✗ Error: {str(e)}[/bold red]")
            raise typer.Exit(code=1)

        # Validate entity type
        entity_type_enum = None
        if entity_type:
            try:
                entity_type_enum = EntityType(entity_type)
            except ValueError:
                console.print(f"[bold red]✗ Invalid entity type: {entity_type}[/bold red]")
                console.print("Valid types: contact, company, deal")
                raise typer.Exit(code=1)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Recalculating scores...", total=None)

            stats = engine.recalculate_all_scores(
                entity_type=entity_type_enum, min_events=min_events
            )

            progress.update(task, completed=True)

        # Display results
        console.print("\n[bold green]✓ Recalculation complete![/bold green]\n")

        table = Table(title="Recalculation Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="magenta", justify="right")

        table.add_row("Total Entities", str(stats["total_entities"]))
        table.add_row("Recalculated", str(stats["recalculated"]))
        table.add_row("Skipped", str(stats["skipped"]))
        table.add_row("Errors", str(stats["errors"]))

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]✗ Error: {str(e)}[/bold red]")
        logger.exception("Recalculation failed")
        raise typer.Exit(code=1)
    finally:
        db.close()


@app.command()
def top_contacts(
    limit: int = typer.Option(50, help="Number of contacts to show"),
    min_score: Optional[float] = typer.Option(None, help="Minimum score threshold"),
    entity_type: Optional[str] = typer.Option("contact", help="Entity type (contact/company/deal)"),
) -> None:
    """Show top engaged contacts."""
    db = get_session()
    try:
        # Validate entity type
        try:
            entity_type_enum = EntityType(entity_type) if entity_type else None
        except ValueError:
            console.print(f"[bold red]✗ Invalid entity type: {entity_type}[/bold red]")
            raise typer.Exit(code=1)

        repo = EngagementRepository(db)
        entities = repo.get_top_contacts(
            limit=limit, min_score=min_score, entity_type=entity_type_enum
        )

        if not entities:
            console.print("[yellow]No entities found matching criteria[/yellow]")
            return

        # Display results
        table = Table(title=f"Top {len(entities)} Engaged {entity_type.title()}s")
        table.add_column("Rank", style="dim", justify="right")
        table.add_column("External ID", style="cyan")
        table.add_column("Score", style="magenta", justify="right")
        table.add_column("Last Activity", style="green")
        table.add_column("Events", justify="right")

        for idx, entity in enumerate(entities, 1):
            last_activity = (
                entity.last_activity_at.strftime("%Y-%m-%d %H:%M")
                if entity.last_activity_at
                else "N/A"
            )

            total_events = entity.score_breakdown.get("total_events", 0) if entity.score_breakdown else 0

            table.add_row(
                str(idx),
                entity.external_id,
                f"{entity.latest_score:.2f}",
                last_activity,
                str(total_events),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]✗ Error: {str(e)}[/bold red]")
        raise typer.Exit(code=1)
    finally:
        db.close()


@app.command()
def stats() -> None:
    """Show overall engagement statistics."""
    db = get_session()
    try:
        repo = EngagementRepository(db)
        statistics = repo.get_statistics()

        console.print("\n[bold blue]Engagement Tracker Statistics[/bold blue]\n")

        # Overall stats
        table = Table(title="Overall Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta", justify="right")

        table.add_row("Total Entities", str(statistics["total_entities"]))
        table.add_row("Total Events", str(statistics["total_events"]))
        table.add_row("Average Score", f"{statistics['average_score']:.2f}")
        table.add_row("Active (Last 30 Days)", str(statistics["active_last_30_days"]))

        console.print(table)

        # By entity type
        if statistics["by_entity_type"]:
            console.print("\n[bold]By Entity Type:[/bold]\n")

            type_table = Table()
            type_table.add_column("Entity Type", style="cyan")
            type_table.add_column("Count", style="magenta", justify="right")

            for entity_type, count in statistics["by_entity_type"].items():
                type_table.add_row(entity_type, str(count))

            console.print(type_table)

    except Exception as e:
        console.print(f"[bold red]✗ Error: {str(e)}[/bold red]")
        raise typer.Exit(code=1)
    finally:
        db.close()


@app.command()
def test_sources() -> None:
    """Test connections to all configured event sources."""
    console.print("[bold blue]Testing source connections...[/bold blue]\n")

    db = get_session()
    try:
        manager = SourceManager(db)
        results = manager.test_all_connections()

        table = Table(title="Source Connection Tests")
        table.add_column("Source", style="cyan")
        table.add_column("Status", justify="center")

        for source_name, status in results.items():
            status_text = "[green]✓ Connected[/green]" if status else "[red]✗ Failed[/red]"
            table.add_row(source_name, status_text)

        console.print(table)

        all_ok = all(results.values())
        if all_ok:
            console.print("\n[bold green]All sources connected successfully![/bold green]")
        else:
            console.print("\n[bold yellow]Some sources failed to connect[/bold yellow]")

    except Exception as e:
        console.print(f"[bold red]✗ Error: {str(e)}[/bold red]")
        raise typer.Exit(code=1)
    finally:
        db.close()


if __name__ == "__main__":
    app()
