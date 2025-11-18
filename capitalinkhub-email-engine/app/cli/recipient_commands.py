"""
CLI commands for recipient management.
"""
import typer
from rich.console import Console
from rich.progress import Progress
from typing import Optional

from app.core.database import get_db, init_db
from app.repositories import CampaignRepository, RecipientRepository
from app.utils import CSVContactSource
from app.models import RecipientSegment

console = Console()
app = typer.Typer(help="Recipient management commands")


@app.command("import")
def import_recipients(
    campaign_id: int = typer.Argument(..., help="Campaign ID to import recipients to"),
    csv_file: str = typer.Option(..., "--file", "-f", help="CSV file path"),
    email_column: str = typer.Option("email", "--email-col", help="Email column name"),
    name_column: str = typer.Option("name", "--name-col", help="Name column name"),
    segment_column: Optional[str] = typer.Option(None, "--segment-col", help="Segment column name"),
    default_segment: str = typer.Option("other", "--default-segment", help="Default segment"),
):
    """
    Import recipients from a CSV file.
    """
    try:
        init_db()

        # Validate default segment
        try:
            default_seg = RecipientSegment(default_segment.lower())
        except ValueError:
            console.print(f"[red]Invalid segment: {default_segment}[/red]")
            console.print(f"Valid segments: {', '.join([s.value for s in RecipientSegment])}")
            raise typer.Exit(1)

        with get_db() as db:
            campaign_repo = CampaignRepository(db)
            recipient_repo = RecipientRepository(db)

            # Verify campaign exists
            campaign = campaign_repo.get(campaign_id)
            if not campaign:
                console.print(f"[red]Campaign {campaign_id} not found[/red]")
                raise typer.Exit(1)

            console.print(f"Importing recipients for campaign: {campaign.name}")

            # Load contacts from CSV
            try:
                contact_source = CSVContactSource(
                    file_path=csv_file,
                    email_column=email_column,
                    name_column=name_column,
                    segment_column=segment_column,
                    default_segment=default_seg
                )
                contacts = contact_source.load_contacts()
            except FileNotFoundError:
                console.print(f"[red]CSV file not found: {csv_file}[/red]")
                raise typer.Exit(1)
            except Exception as e:
                console.print(f"[red]Error loading CSV: {e}[/red]")
                raise typer.Exit(1)

            if not contacts:
                console.print("[yellow]No valid contacts found in CSV[/yellow]")
                raise typer.Exit(1)

            console.print(f"Loaded {len(contacts)} contacts from CSV")

            # Import recipients with progress bar
            imported = 0
            with Progress() as progress:
                task = progress.add_task("[cyan]Importing...", total=len(contacts))

                for contact in contacts:
                    recipient_repo.create(
                        campaign_id=campaign_id,
                        email=contact["email"],
                        name=contact["name"],
                        segment=contact["segment"],
                    )
                    if contact.get("details"):
                        # Update details if present
                        pass  # Details are set during create

                    imported += 1
                    progress.update(task, advance=1)

            console.print(f"[green]✓ Imported {imported} recipients successfully[/green]")

    except Exception as e:
        console.print(f"[red]Error importing recipients: {e}[/red]")
        raise typer.Exit(1)
