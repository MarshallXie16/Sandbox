"""
CLI commands for database operations.
"""
import typer
from rich.console import Console
from rich.prompt import Confirm

from app.core.database import init_db, engine, Base
from app.core.config import settings
from app.repositories import RateLimitRepository
from app.core.database import get_db

console = Console()
app = typer.Typer(help="Database management commands")


@app.command("init")
def initialize_database(
    force: bool = typer.Option(False, "--force", help="Force initialization (drop existing tables)")
):
    """
    Initialize the database schema.
    """
    try:
        if force:
            if not Confirm.ask(
                "[red]This will drop all existing tables. Are you sure?[/red]"
            ):
                raise typer.Exit(0)

            console.print("Dropping existing tables...")
            Base.metadata.drop_all(bind=engine)

        console.print("Initializing database...")
        init_db()

        # Create default rate limit profile
        with get_db() as db:
            rate_limit_repo = RateLimitRepository(db)
            profile = rate_limit_repo.get_or_create_default(settings)

            console.print(f"[green]✓ Database initialized successfully[/green]")
            console.print(f"  Database: {settings.database_url}")
            console.print(f"  Default rate limit profile created:")
            console.print(f"    - Max per hour: {profile.max_per_hour}")
            console.print(f"    - Max per day: {profile.max_per_day}")

    except Exception as e:
        console.print(f"[red]Error initializing database: {e}[/red]")
        raise typer.Exit(1)


@app.command("create-rate-limit")
def create_rate_limit_profile(
    name: str = typer.Option(..., "--name", "-n", help="Profile name"),
    max_per_hour: int = typer.Option(..., "--max-hour", help="Max emails per hour"),
    max_per_day: int = typer.Option(..., "--max-day", help="Max emails per day"),
    min_delay: int = typer.Option(2, "--min-delay", help="Min delay between emails (seconds)"),
    max_delay: int = typer.Option(7, "--max-delay", help="Max delay between emails (seconds)"),
):
    """
    Create a new rate limit profile.
    """
    try:
        init_db()

        with get_db() as db:
            rate_limit_repo = RateLimitRepository(db)

            # Check if profile exists
            existing = rate_limit_repo.get_by_name(name)
            if existing:
                console.print(f"[red]Rate limit profile '{name}' already exists[/red]")
                raise typer.Exit(1)

            # Create profile
            profile = rate_limit_repo.create(
                name=name,
                max_per_hour=max_per_hour,
                max_per_day=max_per_day,
                min_delay_seconds=min_delay,
                max_delay_seconds=max_delay
            )

            console.print(f"[green]✓ Rate limit profile created successfully[/green]")
            console.print(f"  Name: {profile.name}")
            console.print(f"  Max per hour: {profile.max_per_hour}")
            console.print(f"  Max per day: {profile.max_per_day}")
            console.print(f"  Delay range: {profile.min_delay_seconds}-{profile.max_delay_seconds}s")

    except Exception as e:
        console.print(f"[red]Error creating rate limit profile: {e}[/red]")
        raise typer.Exit(1)
