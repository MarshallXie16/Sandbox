"""
Main CLI application.
"""
import typer
from rich.console import Console

from app.core.logging import setup_logging
from . import campaign_commands, recipient_commands, worker_commands, db_commands

# Initialize console for rich output
console = Console()

# Create main app
app = typer.Typer(
    name="email-engine",
    help="Capital Ink Hub Email Campaign Engine",
    add_completion=False,
)

# Set up logging
logger = setup_logging()

# Register subcommands
app.add_typer(campaign_commands.app, name="campaign")
app.add_typer(recipient_commands.app, name="recipient")
app.add_typer(worker_commands.app, name="worker")
app.add_typer(db_commands.app, name="db")


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print("Capital Ink Hub Email Campaign Engine v1.0.0")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    )
):
    """
    Capital Ink Hub Email Campaign Engine.

    A modular email campaign engine for cold outreach, member emails, and warm lead follow-ups.
    """
    pass


if __name__ == "__main__":
    app()
