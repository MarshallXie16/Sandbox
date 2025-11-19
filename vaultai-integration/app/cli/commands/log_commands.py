"""
VaultAI Integration Layer - Log CLI Commands
"""

import asyncio
import typer
from rich.console import Console
from rich.table import Table
from datetime import datetime, timedelta

app = typer.Typer()
console = Console()


@app.command()
def recent(
    limit: int = typer.Option(10, help="Number of logs to show"),
    domain: str = typer.Option(None, help="Filter by domain"),
):
    """Show recent LLM logs."""
    from app.core.database import AsyncSessionLocal
    from app.models import LLMLog
    from sqlalchemy import select, desc

    async def run():
        async with AsyncSessionLocal() as db:
            query = select(LLMLog).order_by(desc(LLMLog.created_at)).limit(limit)

            if domain:
                query = query.where(LLMLog.domain == domain)

            result = await db.execute(query)
            logs = result.scalars().all()

            if not logs:
                console.print("[yellow]No logs found[/yellow]")
                return

            table = Table(title=f"Recent LLM Logs (Last {limit})")
            table.add_column("ID", style="cyan")
            table.add_column("Domain", style="yellow")
            table.add_column("Task", style="green")
            table.add_column("Provider", style="magenta")
            table.add_column("Tokens", style="blue")
            table.add_column("Latency (ms)", style="white")
            table.add_column("Status", style="green")

            for log in logs:
                table.add_row(
                    str(log.id),
                    log.domain or "N/A",
                    log.task_type or "N/A",
                    log.provider,
                    str(log.total_tokens or "N/A"),
                    f"{log.latency_ms:.0f}" if log.latency_ms else "N/A",
                    log.status,
                )

            console.print(table)

    asyncio.run(run())


@app.command()
def stats(
    days: int = typer.Option(7, help="Number of days to analyze"),
):
    """Show usage statistics."""
    from app.core.database import AsyncSessionLocal
    from app.models import LLMLog
    from sqlalchemy import select, func

    async def run():
        async with AsyncSessionLocal() as db:
            # Calculate date range
            since = datetime.utcnow() - timedelta(days=days)

            # Total requests
            result = await db.execute(
                select(func.count(LLMLog.id)).where(LLMLog.created_at >= since)
            )
            total_requests = result.scalar()

            # Total tokens
            result = await db.execute(
                select(func.sum(LLMLog.total_tokens)).where(LLMLog.created_at >= since)
            )
            total_tokens = result.scalar() or 0

            # Average latency
            result = await db.execute(
                select(func.avg(LLMLog.latency_ms)).where(LLMLog.created_at >= since)
            )
            avg_latency = result.scalar() or 0

            # By provider
            result = await db.execute(
                select(LLMLog.provider, func.count(LLMLog.id))
                .where(LLMLog.created_at >= since)
                .group_by(LLMLog.provider)
            )
            by_provider = result.all()

            console.print(f"[bold cyan]Usage Statistics (Last {days} days)[/bold cyan]")
            console.print(f"Total Requests: {total_requests}")
            console.print(f"Total Tokens: {total_tokens:,}")
            console.print(f"Average Latency: {avg_latency:.0f}ms")
            console.print("\n[bold]By Provider:[/bold]")
            for provider, count in by_provider:
                console.print(f"  {provider}: {count} requests")

    asyncio.run(run())
