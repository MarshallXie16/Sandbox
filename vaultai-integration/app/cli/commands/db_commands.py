"""
VaultAI Integration Layer - Database CLI Commands
"""

import asyncio
import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def init():
    """Initialize database tables."""
    from app.core.database import init_db

    async def run():
        await init_db()
        console.print("[green]✓ Database initialized[/green]")

    asyncio.run(run())


@app.command()
def reset():
    """Reset database (drop all tables and recreate)."""
    from app.core.database import engine, Base

    confirm = typer.confirm("⚠️  This will delete all data. Continue?")
    if not confirm:
        console.print("[yellow]Cancelled[/yellow]")
        return

    async def run():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            console.print("[yellow]Tables dropped[/yellow]")
            await conn.run_sync(Base.metadata.create_all)
            console.print("[green]Tables recreated[/green]")

    asyncio.run(run())


@app.command()
def stats():
    """Show database statistics."""
    from app.core.database import AsyncSessionLocal
    from app.models import LLMLog, PromptTemplate, Document, Embedding
    from sqlalchemy import select, func

    async def run():
        async with AsyncSessionLocal() as db:
            # Count LLM logs
            result = await db.execute(select(func.count(LLMLog.id)))
            llm_logs_count = result.scalar()

            # Count templates
            result = await db.execute(select(func.count(PromptTemplate.id)))
            templates_count = result.scalar()

            # Count documents
            result = await db.execute(select(func.count(Document.id)))
            documents_count = result.scalar()

            # Count embeddings
            result = await db.execute(select(func.count(Embedding.id)))
            embeddings_count = result.scalar()

            console.print("[bold cyan]Database Statistics[/bold cyan]")
            console.print(f"LLM Logs: {llm_logs_count}")
            console.print(f"Prompt Templates: {templates_count}")
            console.print(f"Documents: {documents_count}")
            console.print(f"Embeddings: {embeddings_count}")

    asyncio.run(run())
