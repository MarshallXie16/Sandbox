#!/usr/bin/env python3
"""
Portal CLI - Command-line tool for portal API management.

Usage:
    python portal_cli.py portal init-db
    python portal_cli.py portal create-api-key
    python portal_cli.py members list
    python portal_cli.py members find --um-user-id 123 --email user@example.com
"""

import sys
import asyncio
import secrets
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.database import get_engine
from app.core.database import Base
from app.repositories import PortalMembersRepository, ContactsRepository
from app.services import ProfileService
from app.schemas.member import MemberResolveRequest

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create Typer app
app = typer.Typer(help="Portal API CLI tool")
console = Console()


# Portal commands
portal_app = typer.Typer(help="Portal management commands")
app.add_typer(portal_app, name="portal")


@portal_app.command("init-db")
def init_db():
    """
    Initialize database tables.

    Creates all portal-specific tables (portal_members, portal_interests, portal_resources).
    Note: CRM tables should already exist in IndieStack CRM database.
    """
    console.print("[bold blue]Initializing database...[/bold blue]")

    async def _init():
        engine = get_engine()
        async with engine.begin() as conn:
            # Create portal-specific tables only
            # (CRM tables should already exist)
            await conn.run_sync(Base.metadata.create_all)

        console.print("[bold green]✓ Database tables created successfully[/bold green]")

    asyncio.run(_init())


@portal_app.command("create-api-key")
def create_api_key():
    """
    Generate a new API key for WordPress/Ultimate Member integration.
    """
    api_key = secrets.token_urlsafe(32)

    console.print("\n[bold green]Generated API Key:[/bold green]")
    console.print(f"\n  {api_key}\n")
    console.print("[yellow]Add this to your .env file as PORTAL_API_KEY or PORTAL_API_KEYS[/yellow]")
    console.print("[yellow]Add this to WordPress/Ultimate Member configuration[/yellow]\n")


# Member commands
members_app = typer.Typer(help="Member management commands")
app.add_typer(members_app, name="members")


@members_app.command("list")
def list_members(
    limit: int = typer.Option(20, help="Maximum number of members to display"),
    role: Optional[str] = typer.Option(None, help="Filter by role (buyer/seller/both)"),
):
    """
    List portal members.
    """
    console.print(f"[bold blue]Listing portal members (limit: {limit})...[/bold blue]\n")

    async def _list():
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.core.database import get_session_maker

        session_maker = get_session_maker()
        async with session_maker() as session:
            repo = PortalMembersRepository(session)
            members = await repo.get_active_members(role=role, limit=limit)

            if not members:
                console.print("[yellow]No members found[/yellow]")
                return

            table = Table(title=f"Portal Members ({len(members)} found)")
            table.add_column("ID", style="cyan")
            table.add_column("UM User ID", style="magenta")
            table.add_column("Contact ID", style="green")
            table.add_column("Role", style="yellow")
            table.add_column("Active", style="blue")

            for member in members:
                table.add_row(
                    str(member.id),
                    member.um_user_id,
                    str(member.contact_id),
                    member.role,
                    "✓" if member.is_active else "✗",
                )

            console.print(table)

    asyncio.run(_list())


@members_app.command("find")
def find_member(
    um_user_id: Optional[str] = typer.Option(None, help="Ultimate Member user ID"),
    email: Optional[str] = typer.Option(None, help="Email address"),
):
    """
    Find or resolve a member mapping.

    This uses the same resolution logic as the API endpoint.
    """
    if not um_user_id and not email:
        console.print("[red]Error: Must provide --um-user-id or --email[/red]")
        raise typer.Exit(1)

    console.print("[bold blue]Resolving member...[/bold blue]\n")

    async def _find():
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.core.database import get_session_maker

        session_maker = get_session_maker()
        async with session_maker() as session:
            if um_user_id:
                # Try direct lookup
                repo = PortalMembersRepository(session)
                member = await repo.get_by_um_user_id(um_user_id)

                if member:
                    console.print(f"[green]✓ Found existing member mapping:[/green]")
                    console.print(f"  Member ID: {member.id}")
                    console.print(f"  UM User ID: {member.um_user_id}")
                    console.print(f"  Contact ID: {member.contact_id}")
                    console.print(f"  Role: {member.role}")
                else:
                    console.print(f"[yellow]No mapping found for UM user ID: {um_user_id}[/yellow]")

            if email:
                # Try contact lookup
                contacts_repo = ContactsRepository(session)
                contact = await contacts_repo.get_by_email(email)

                if contact:
                    console.print(f"\n[green]✓ Found contact:[/green]")
                    console.print(f"  Contact ID: {contact.id}")
                    console.print(f"  Name: {contact.first_name} {contact.last_name}")
                    console.print(f"  Email: {contact.primary_email}")
                    console.print(f"  Category: {contact.category}")
                else:
                    console.print(f"\n[yellow]No contact found for email: {email}[/yellow]")

    asyncio.run(_find())


if __name__ == "__main__":
    app()
