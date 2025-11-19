"""
VaultAI Integration Layer - CLI
Command-line interface for administrative operations.
"""

import typer
from rich.console import Console
from rich.table import Table

from app.cli.commands import (
    db_commands,
    provider_commands,
    template_commands,
    log_commands,
)

app = typer.Typer(
    name="vaultai",
    help="VaultAI Integration Layer CLI",
    add_completion=False,
)

console = Console()

# Register command groups
app.add_typer(db_commands.app, name="db", help="Database operations")
app.add_typer(provider_commands.app, name="provider", help="LLM provider management")
app.add_typer(template_commands.app, name="template", help="Prompt template management")
app.add_typer(log_commands.app, name="logs", help="View and analyze logs")


@app.command()
def version():
    """Show version information."""
    console.print("[bold green]VaultAI Integration Layer[/bold green]")
    console.print("Version: [cyan]1.0.0[/cyan]")
    console.print("Module: [cyan]10 - AI Gateway[/cyan]")


@app.command()
def status():
    """Show service status."""
    from app.core.config import settings
    from app.llm.router import llm_router

    table = Table(title="VaultAI Service Status")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Environment", settings.VAULTAI_ENV)
    table.add_row("Debug Mode", str(settings.VAULTAI_DEBUG))
    table.add_row("Default Provider", settings.LLM_DEFAULT_PROVIDER)
    table.add_row("PII Redaction", str(settings.ENABLE_PII_REDACTION))
    table.add_row("Rate Limiting", str(settings.RATE_LIMIT_ENABLED))

    console.print(table)

    # Show providers
    provider_table = Table(title="LLM Providers")
    provider_table.add_column("Provider", style="cyan")
    provider_table.add_column("Status", style="green")
    provider_table.add_column("Model", style="yellow")

    for provider_name, client in llm_router.providers.items():
        provider_table.add_row(
            provider_name,
            "✓ Configured",
            client.config.model,
        )

    console.print(provider_table)


if __name__ == "__main__":
    app()
