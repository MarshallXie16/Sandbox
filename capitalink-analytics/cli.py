#!/usr/bin/env python3
"""CLI entry point for Capitalink Analytics."""

import asyncio
from datetime import date
from typing import Optional

import typer
from rich.console import Console

from app.cli.commands import (
    crm_overview,
    exit_ready_summary,
    facilitator_funnel,
    facilitator_revenue,
    run_snapshot,
)

app = typer.Typer(
    name="analytics",
    help="Capitalink Analytics CLI - Analytics and reporting commands",
)

console = Console()


# Snapshot commands
@app.command("snapshot")
def snapshot(
    snapshot_date: str = typer.Option(
        None,
        "--date",
        "-d",
        help="Snapshot date (YYYY-MM-DD). Defaults to today.",
    ),
    domain: Optional[str] = typer.Option(
        None,
        "--domain",
        help="Specific domain to snapshot (exit_ready, facilitator, crm)",
    ),
):
    """
    Run analytics snapshot to collect and store metrics.

    Examples:
        analytics snapshot --date 2025-01-15
        analytics snapshot --date 2025-01-15 --domain exit_ready
    """
    if not snapshot_date:
        snapshot_date = date.today().isoformat()

    asyncio.run(run_snapshot(snapshot_date, domain))


# Exit Ready commands
@app.command("exit-ready")
def exit_ready():
    """Display Exit Ready analytics summary."""
    asyncio.run(exit_ready_summary())


# Facilitator commands
facilitator_app = typer.Typer(
    name="facilitator",
    help="Facilitator analytics commands",
)


@facilitator_app.command("revenue")
def revenue(
    from_date: Optional[str] = typer.Option(
        None,
        "--from",
        help="Start date (YYYY-MM-DD)",
    ),
    to_date: Optional[str] = typer.Option(
        None,
        "--to",
        help="End date (YYYY-MM-DD)",
    ),
):
    """
    Display Facilitator revenue summary.

    Examples:
        analytics facilitator revenue
        analytics facilitator revenue --from 2025-01-01 --to 2025-01-31
    """
    asyncio.run(facilitator_revenue(from_date, to_date))


@facilitator_app.command("funnel")
def funnel():
    """Display Facilitator buyer introduction funnel."""
    asyncio.run(facilitator_funnel())


app.add_typer(facilitator_app, name="facilitator")


# CRM commands
@app.command("crm")
def crm():
    """Display CRM overview statistics."""
    asyncio.run(crm_overview())


if __name__ == "__main__":
    app()
