"""
CLI command implementations for Facilitator Automation.
"""

import typer
import asyncio
from rich.console import Console
from rich.table import Table
from decimal import Decimal
from datetime import datetime

from app.core.database import AsyncSessionLocal
from app.core.logging import setup_logging
from app.models.enums import EngagementStatus, BuyerIntroStatus, OfferStatus
from app.schemas import (
    EngagementCreate, BuyerIntroCreate, OfferCreate, ClosingCreate, IntroductionChannel
)
from app.services import EngagementService, BuyerIntroService, OfferService, ClosingService

console = Console()
setup_logging()

# Create Typer apps for each command group
engagements = typer.Typer()
buyers = typer.Typer()
offers = typer.Typer()
closings = typer.Typer()


# ============================================================================
# ENGAGEMENT COMMANDS
# ============================================================================

@engagements.command("list")
def list_engagements(
    status: str = typer.Option(None, help="Filter by status"),
    seller_contact_id: int = typer.Option(None, help="Filter by seller contact ID")
):
    """List all engagements."""
    async def _list():
        async with AsyncSessionLocal() as db:
            service = EngagementService(db)
            status_enum = EngagementStatus(status) if status else None
            items = await service.list_engagements(
                status=status_enum,
                seller_contact_id=seller_contact_id
            )

            table = Table(title="Facilitator Engagements")
            table.add_column("ID", style="cyan")
            table.add_column("Code", style="magenta")
            table.add_column("Status", style="green")
            table.add_column("Seller ID", style="yellow")
            table.add_column("Created", style="blue")

            for item in items:
                table.add_row(
                    str(item.id),
                    item.engagement_code,
                    item.status.value,
                    str(item.seller_contact_id),
                    item.created_at.strftime("%Y-%m-%d")
                )

            console.print(table)

    asyncio.run(_list())


@engagements.command("create")
def create_engagement(
    seller_contact_id: int = typer.Option(..., help="Seller contact ID"),
    company_id: int = typer.Option(None, help="Company ID"),
    listing_id: int = typer.Option(None, help="Listing ID")
):
    """Create a new facilitator engagement."""
    async def _create():
        async with AsyncSessionLocal() as db:
            service = EngagementService(db)
            data = EngagementCreate(
                seller_contact_id=seller_contact_id,
                company_id=company_id,
                listing_id=listing_id
            )
            engagement = await service.create_engagement(data)
            console.print(
                f"[green]Created engagement {engagement.engagement_code} "
                f"(ID: {engagement.id})[/green]"
            )

    asyncio.run(_create())


@engagements.command("activate")
def activate_engagement(engagement_id: int = typer.Argument(..., help="Engagement ID")):
    """Activate an engagement."""
    async def _activate():
        async with AsyncSessionLocal() as db:
            service = EngagementService(db)
            engagement = await service.activate_engagement(engagement_id)
            console.print(
                f"[green]Activated engagement {engagement.engagement_code} "
                f"(status: {engagement.status.value})[/green]"
            )

    asyncio.run(_activate())


@engagements.command("summary")
def engagement_summary(engagement_id: int = typer.Argument(..., help="Engagement ID")):
    """Show detailed engagement summary."""
    async def _summary():
        async with AsyncSessionLocal() as db:
            service = EngagementService(db)
            engagement = await service.get_engagement_with_relations(engagement_id)

            if not engagement:
                console.print(f"[red]Engagement {engagement_id} not found[/red]")
                return

            console.print(f"\n[bold cyan]Engagement {engagement.engagement_code}[/bold cyan]")
            console.print(f"Status: [green]{engagement.status.value}[/green]")
            console.print(f"Seller Contact ID: {engagement.seller_contact_id}")
            console.print(f"Offer Fee: ${engagement.offer_fee_fixed:,.2f}")
            console.print(f"Success Fee Rate: {float(engagement.success_fee_rate) * 100}%")

            console.print(f"\n[bold]Introduced Buyers:[/bold] {len(engagement.buyer_intros)}")
            console.print(f"[bold]Offers:[/bold] {len(engagement.offers)}")
            console.print(f"[bold]Closings:[/bold] {len(engagement.closings)}")

    asyncio.run(_summary())


# ============================================================================
# BUYER COMMANDS
# ============================================================================

@buyers.command("add")
def add_buyer(
    engagement_id: int = typer.Option(..., help="Engagement ID"),
    buyer_contact_id: int = typer.Option(..., help="Buyer contact ID"),
    channel: str = typer.Option("email", help="Introduction channel")
):
    """Introduce a buyer to an engagement."""
    async def _add():
        async with AsyncSessionLocal() as db:
            service = BuyerIntroService(db)
            data = BuyerIntroCreate(
                buyer_contact_id=buyer_contact_id,
                introduction_channel=IntroductionChannel(channel)
            )
            buyer_intro = await service.introduce_buyer(engagement_id, data)
            console.print(
                f"[green]Introduced buyer {buyer_contact_id} to engagement "
                f"{engagement_id} (buyer_intro_id: {buyer_intro.id})[/green]"
            )

    asyncio.run(_add())


@buyers.command("list")
def list_buyers(engagement_id: int = typer.Argument(..., help="Engagement ID")):
    """List buyers for an engagement."""
    async def _list():
        async with AsyncSessionLocal() as db:
            service = BuyerIntroService(db)
            items = await service.list_by_engagement(engagement_id)

            table = Table(title=f"Buyers for Engagement {engagement_id}")
            table.add_column("ID", style="cyan")
            table.add_column("Buyer Contact ID", style="magenta")
            table.add_column("Status", style="green")
            table.add_column("Channel", style="yellow")
            table.add_column("Introduced", style="blue")

            for item in items:
                table.add_row(
                    str(item.id),
                    str(item.buyer_contact_id),
                    item.status.value,
                    item.introduction_channel.value,
                    item.introduced_at.strftime("%Y-%m-%d")
                )

            console.print(table)

    asyncio.run(_list())


@buyers.command("set-status")
def set_buyer_status(
    buyer_intro_id: int = typer.Argument(..., help="Buyer intro ID"),
    status: str = typer.Argument(..., help="New status")
):
    """Set buyer intro status."""
    async def _set_status():
        async with AsyncSessionLocal() as db:
            service = BuyerIntroService(db)
            buyer_intro = await service.set_status(
                buyer_intro_id,
                BuyerIntroStatus(status)
            )
            console.print(
                f"[green]Updated buyer intro {buyer_intro_id} "
                f"status to {buyer_intro.status.value}[/green]"
            )

    asyncio.run(_set_status())


# ============================================================================
# OFFER COMMANDS
# ============================================================================

@offers.command("add")
def add_offer(
    engagement_id: int = typer.Option(..., help="Engagement ID"),
    buyer_intro_id: int = typer.Option(..., help="Buyer intro ID"),
    headline_price: float = typer.Option(..., help="Offer price")
):
    """Record an offer from a buyer."""
    async def _add():
        async with AsyncSessionLocal() as db:
            service = OfferService(db)
            data = OfferCreate(
                buyer_intro_id=buyer_intro_id,
                offer_date=datetime.now(),
                headline_price=Decimal(str(headline_price))
            )
            offer = await service.create_offer(engagement_id, data)
            console.print(
                f"[green]Recorded offer {offer.id}: ${offer.headline_price:,.2f} "
                f"from buyer_intro {buyer_intro_id}[/green]"
            )

    asyncio.run(_add())


@offers.command("list")
def list_offers(engagement_id: int = typer.Argument(..., help="Engagement ID")):
    """List offers for an engagement."""
    async def _list():
        async with AsyncSessionLocal() as db:
            service = OfferService(db)
            items = await service.list_by_engagement(engagement_id)

            table = Table(title=f"Offers for Engagement {engagement_id}")
            table.add_column("ID", style="cyan")
            table.add_column("Buyer Intro ID", style="magenta")
            table.add_column("Price", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Offer Fee", style="blue")

            for item in items:
                table.add_row(
                    str(item.id),
                    str(item.buyer_intro_id),
                    f"${item.headline_price:,.2f}",
                    item.status.value,
                    f"${item.offer_fee_amount:,.2f}"
                )

            console.print(table)

    asyncio.run(_list())


# ============================================================================
# CLOSING COMMANDS
# ============================================================================

@closings.command("record")
def record_closing(
    engagement_id: int = typer.Option(..., help="Engagement ID"),
    buyer_intro_id: int = typer.Option(..., help="Buyer intro ID (MUST be introduced)"),
    final_price: float = typer.Option(..., help="Final transaction price")
):
    """Record a deal closing with fee calculation."""
    async def _record():
        async with AsyncSessionLocal() as db:
            service = ClosingService(db)
            data = ClosingCreate(
                buyer_intro_id=buyer_intro_id,
                closing_date=datetime.now(),
                final_price=Decimal(str(final_price))
            )
            closing = await service.record_closing(engagement_id, data)

            console.print(f"\n[bold green]Closing Recorded Successfully![/bold green]")
            console.print(f"Closing ID: {closing.id}")
            console.print(f"Final Price: ${closing.final_price:,.2f}")
            console.print(f"\n[bold]Fee Calculation:[/bold]")
            console.print(f"  Success Fee Rate: {float(closing.success_fee_rate) * 100}%")
            console.print(f"  Gross Success Fee: ${closing.success_fee_gross_amount:,.2f}")
            console.print(f"  Offer Fee Credit: -${closing.offer_fee_credit_amount:,.2f}")
            console.print(f"  [green bold]Net Success Fee: ${closing.success_fee_net_amount:,.2f}[/green bold]")

    asyncio.run(_record())


@closings.command("show")
def show_closing(engagement_id: int = typer.Argument(..., help="Engagement ID")):
    """Show closing details for an engagement."""
    async def _show():
        async with AsyncSessionLocal() as db:
            service = ClosingService(db)
            closing = await service.get_by_engagement(engagement_id)

            if not closing:
                console.print(f"[yellow]No closing found for engagement {engagement_id}[/yellow]")
                return

            console.print(f"\n[bold cyan]Closing for Engagement {engagement_id}[/bold cyan]")
            console.print(f"Closing Date: {closing.closing_date.strftime('%Y-%m-%d')}")
            console.print(f"Final Price: ${closing.final_price:,.2f}")
            console.print(f"Buyer Intro ID: {closing.buyer_intro_id}")
            console.print(f"\n[bold]Fees:[/bold]")
            console.print(f"  Gross: ${closing.success_fee_gross_amount:,.2f}")
            console.print(f"  Credit: ${closing.offer_fee_credit_amount:,.2f}")
            console.print(f"  Net: ${closing.success_fee_net_amount:,.2f}")
            console.print(f"\n[bold]Status:[/bold]")
            console.print(f"  Invoiced: {'Yes' if closing.invoiced else 'No'}")
            console.print(f"  Paid: {'Yes' if closing.paid else 'No'}")

    asyncio.run(_show())
