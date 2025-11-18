"""
CLI commands for campaign management.
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from datetime import datetime
from typing import Optional

from app.core.database import get_db, init_db
from app.models import CampaignType, CampaignStatus, EmailBackend
from app.repositories import CampaignRepository, RateLimitRepository, RecipientRepository
from app.core.config import settings
from app.utils import EmailRenderer

console = Console()
app = typer.Typer(help="Campaign management commands")


@app.command("create")
def create_campaign(
    name: str = typer.Option(..., "--name", "-n", help="Campaign name"),
    campaign_type: str = typer.Option(..., "--type", "-t", help="Campaign type (cold/member/warm)"),
    subject: str = typer.Option(..., "--subject", "-s", help="Subject line template"),
    template: str = typer.Option(..., "--template", help="Body template file path"),
    sender_name: str = typer.Option(..., "--sender-name", help="Sender name"),
    sender_email: str = typer.Option(..., "--sender-email", help="Sender email"),
    backend: str = typer.Option(..., "--backend", "-b", help="Email backend (sendy/smtp)"),
    rate_limit_profile: Optional[str] = typer.Option(None, "--rate-limit", help="Rate limit profile name"),
):
    """
    Create a new email campaign.
    """
    try:
        # Validate inputs
        try:
            camp_type = CampaignType(campaign_type.lower())
        except ValueError:
            console.print(f"[red]Invalid campaign type: {campaign_type}[/red]")
            console.print(f"Valid types: {', '.join([t.value for t in CampaignType])}")
            raise typer.Exit(1)

        try:
            email_backend = EmailBackend(backend.lower())
        except ValueError:
            console.print(f"[red]Invalid backend: {backend}[/red]")
            console.print(f"Valid backends: {', '.join([b.value for b in EmailBackend])}")
            raise typer.Exit(1)

        # Validate template
        renderer = EmailRenderer()
        if not renderer.renderer.template_exists(template):
            console.print(f"[yellow]Warning: Template file not found: {template}[/yellow]")
            if not Confirm.ask("Continue anyway?"):
                raise typer.Exit(1)

        # Validate subject template
        is_valid, error = renderer.validate_template(subject, template)
        if not is_valid:
            console.print(f"[yellow]Warning: Template validation failed: {error}[/yellow]")
            if not Confirm.ask("Continue anyway?"):
                raise typer.Exit(1)

        init_db()

        with get_db() as db:
            campaign_repo = CampaignRepository(db)
            rate_limit_repo = RateLimitRepository(db)

            # Check if campaign name exists
            existing = campaign_repo.get_by_name(name)
            if existing:
                console.print(f"[red]Campaign with name '{name}' already exists[/red]")
                raise typer.Exit(1)

            # Get or create rate limit profile
            if rate_limit_profile:
                profile = rate_limit_repo.get_by_name(rate_limit_profile)
                if not profile:
                    console.print(f"[red]Rate limit profile '{rate_limit_profile}' not found[/red]")
                    raise typer.Exit(1)
            else:
                profile = rate_limit_repo.get_or_create_default(settings)

            # Create campaign
            campaign = campaign_repo.create(
                name=name,
                type=camp_type,
                subject_template=subject,
                body_template_path=template,
                sender_name=sender_name,
                sender_email=sender_email,
                backend=email_backend,
                rate_limit_profile_id=profile.id,
                status=CampaignStatus.DRAFT
            )

            console.print(f"[green]✓ Campaign created successfully[/green]")
            console.print(f"  ID: {campaign.id}")
            console.print(f"  Name: {campaign.name}")
            console.print(f"  Type: {campaign.type.value}")
            console.print(f"  Backend: {campaign.backend.value}")
            console.print(f"  Status: {campaign.status.value}")

    except Exception as e:
        console.print(f"[red]Error creating campaign: {e}[/red]")
        raise typer.Exit(1)


@app.command("list")
def list_campaigns(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
    campaign_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by type"),
):
    """
    List all campaigns.
    """
    try:
        init_db()

        with get_db() as db:
            campaign_repo = CampaignRepository(db)

            if status:
                try:
                    status_filter = CampaignStatus(status.lower())
                    campaigns = campaign_repo.get_by_status(status_filter)
                except ValueError:
                    console.print(f"[red]Invalid status: {status}[/red]")
                    raise typer.Exit(1)
            elif campaign_type:
                try:
                    type_filter = CampaignType(campaign_type.lower())
                    campaigns = campaign_repo.get_by_type(type_filter)
                except ValueError:
                    console.print(f"[red]Invalid type: {campaign_type}[/red]")
                    raise typer.Exit(1)
            else:
                campaigns = campaign_repo.get_all(limit=1000)

            if not campaigns:
                console.print("[yellow]No campaigns found[/yellow]")
                return

            table = Table(title="Campaigns")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Type")
            table.add_column("Status")
            table.add_column("Backend")
            table.add_column("Recipients")
            table.add_column("Created")

            recipient_repo = RecipientRepository(db)
            for campaign in campaigns:
                recipient_count = recipient_repo.count_by_campaign(campaign.id)
                table.add_row(
                    str(campaign.id),
                    campaign.name,
                    campaign.type.value,
                    campaign.status.value,
                    campaign.backend.value,
                    str(recipient_count),
                    campaign.created_at.strftime("%Y-%m-%d %H:%M")
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing campaigns: {e}[/red]")
        raise typer.Exit(1)


@app.command("schedule")
def schedule_campaign(
    campaign_id: int = typer.Argument(..., help="Campaign ID to schedule"),
    when: Optional[str] = typer.Option(None, "--when", help="Schedule time (ISO format or 'now')"),
):
    """
    Schedule a campaign for sending.
    """
    try:
        init_db()

        # Parse schedule time
        if when and when.lower() == "now":
            scheduled_at = datetime.utcnow()
        elif when:
            try:
                scheduled_at = datetime.fromisoformat(when)
            except ValueError:
                console.print(f"[red]Invalid datetime format: {when}[/red]")
                console.print("Use ISO format (YYYY-MM-DD HH:MM:SS) or 'now'")
                raise typer.Exit(1)
        else:
            scheduled_at = datetime.utcnow()

        with get_db() as db:
            campaign_repo = CampaignRepository(db)
            recipient_repo = RecipientRepository(db)

            campaign = campaign_repo.get(campaign_id)
            if not campaign:
                console.print(f"[red]Campaign {campaign_id} not found[/red]")
                raise typer.Exit(1)

            # Check if campaign has recipients
            recipient_count = recipient_repo.count_by_campaign(campaign_id)
            if recipient_count == 0:
                console.print(f"[red]Campaign has no recipients. Import recipients first.[/red]")
                raise typer.Exit(1)

            # Schedule campaign
            campaign_repo.schedule_campaign(campaign, scheduled_at)

            console.print(f"[green]✓ Campaign scheduled successfully[/green]")
            console.print(f"  Campaign: {campaign.name}")
            console.print(f"  Scheduled for: {scheduled_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            console.print(f"  Recipients: {recipient_count}")

    except Exception as e:
        console.print(f"[red]Error scheduling campaign: {e}[/red]")
        raise typer.Exit(1)
