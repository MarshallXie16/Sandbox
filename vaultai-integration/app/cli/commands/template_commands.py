"""
VaultAI Integration Layer - Template CLI Commands
"""

import asyncio
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


@app.command()
def list(domain: str = typer.Option(None, help="Filter by domain")):
    """List prompt templates."""
    from app.core.database import AsyncSessionLocal
    from app.models import PromptTemplate
    from sqlalchemy import select

    async def run():
        async with AsyncSessionLocal() as db:
            query = select(PromptTemplate)
            if domain:
                query = query.where(PromptTemplate.domain == domain)

            result = await db.execute(query)
            templates = result.scalars().all()

            if not templates:
                console.print("[yellow]No templates found[/yellow]")
                return

            table = Table(title="Prompt Templates")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Domain", style="yellow")
            table.add_column("Task Type", style="magenta")
            table.add_column("Version", style="blue")
            table.add_column("Active", style="white")

            for template in templates:
                table.add_row(
                    str(template.id),
                    template.name,
                    template.domain,
                    template.task_type,
                    str(template.version),
                    "✓" if template.is_active else "✗",
                )

            console.print(table)

    asyncio.run(run())


@app.command()
def show(name: str = typer.Argument(..., help="Template name")):
    """Show template details."""
    from app.core.database import AsyncSessionLocal
    from app.models import PromptTemplate
    from sqlalchemy import select

    async def run():
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(PromptTemplate).where(PromptTemplate.name == name)
            )
            template = result.scalar_one_or_none()

            if not template:
                console.print(f"[red]Template '{name}' not found[/red]")
                return

            console.print(f"[bold cyan]Template: {template.name}[/bold cyan]")
            console.print(f"Domain: {template.domain}")
            console.print(f"Task Type: {template.task_type}")
            console.print(f"Version: {template.version}")
            console.print(f"Active: {'Yes' if template.is_active else 'No'}")
            console.print(f"\n[bold]System Prompt:[/bold]")
            console.print(template.system_prompt or "None")
            console.print(f"\n[bold]User Prompt Template:[/bold]")
            console.print(template.user_prompt_template)

    asyncio.run(run())
