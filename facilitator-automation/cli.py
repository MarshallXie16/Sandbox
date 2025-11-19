"""
CLI entrypoint for Facilitator Automation.

Usage:
    python cli.py engagements list
    python cli.py engagements create --seller-contact-id 123 --company-id 456
    python cli.py buyers add --engagement-id 1 --buyer-contact-id 321
    python cli.py closings record --engagement-id 1 --buyer-intro-id 5 --final-price 2500000
"""

import typer
import asyncio
from app.cli.commands import engagements, buyers, offers, closings

app = typer.Typer(
    name="facilitator",
    help="Facilitator Automation CLI - Phase 2 Facilitator Service",
    no_args_is_help=True
)

# Add command groups
app.add_typer(engagements.app, name="engagements", help="Manage facilitator engagements")
app.add_typer(buyers.app, name="buyers", help="Manage buyer introductions")
app.add_typer(offers.app, name="offers", help="Manage offers")
app.add_typer(closings.app, name="closings", help="Manage closings")


if __name__ == "__main__":
    app()
