"""
CLI commands for managing the matching engine.
"""

import asyncio
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from app.config import get_settings
from app.core.matching_engine import MatchingEngine
from app.core.scoring.config import get_scoring_config
from app.database import AsyncSessionLocal

app = typer.Typer(
    name="matching-engine",
    help="Indie Matching Engine CLI - Buyer-Seller matching and scoring",
)
console = Console()


@app.command()
def info():
    """Display configuration and system information."""
    settings = get_settings()
    config = get_scoring_config()

    console.print("\n[bold cyan]Indie Matching Engine - Configuration[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="yellow")

    table.add_row("Database", settings.database_url.split("@")[-1])
    table.add_row("API Port", str(settings.api_port))
    table.add_row("Log Level", settings.log_level)
    table.add_row("Scoring Config", settings.scoring_config_path)
    table.add_row("Min Recommendation Score", str(settings.min_recommendation_score))
    table.add_row("Max Recommendations", str(settings.max_recommendations))
    table.add_row("Cache TTL", f"{settings.cache_ttl_seconds}s")
    table.add_row("Match Caching", "Enabled" if settings.enable_match_caching else "Disabled")
    table.add_row(
        "Engagement Integration",
        "Enabled" if settings.enable_engagement_integration else "Disabled",
    )

    console.print(table)

    console.print("\n[bold cyan]Scoring Weights[/bold cyan]\n")
    weights_table = Table(show_header=True, header_style="bold magenta")
    weights_table.add_column("Component", style="cyan")
    weights_table.add_column("Weight", style="yellow")

    weights_table.add_row("Industry (exact)", str(config.weights.industry_exact))
    weights_table.add_row("Industry (related)", str(config.weights.industry_related))
    weights_table.add_row("Region (exact)", str(config.weights.region_exact))
    weights_table.add_row("Region (nearby)", str(config.weights.region_nearby))
    weights_table.add_row("Deal Size (perfect)", str(config.weights.deal_size_perfect))
    weights_table.add_row("Experience (strong)", str(config.weights.experience_strong))
    weights_table.add_row("Engagement (high)", str(config.weights.engagement_high))

    console.print(weights_table)
    console.print()


@app.command()
def compute_matches(
    buyer_ids: Optional[List[int]] = typer.Option(
        None,
        "--buyer-id",
        "-b",
        help="Specific buyer IDs to process (can be specified multiple times)",
    ),
    listing_ids: Optional[List[int]] = typer.Option(
        None,
        "--listing-id",
        "-l",
        help="Specific listing IDs to process (can be specified multiple times)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force recomputation even if cached scores exist",
    ),
):
    """
    Compute and cache match scores for buyer-listing pairs.

    Examples:
        # Compute matches for all active buyers and listings
        matching-engine compute-matches

        # Compute matches for specific buyer
        matching-engine compute-matches --buyer-id 123

        # Force recomputation
        matching-engine compute-matches --force
    """
    console.print("\n[bold cyan]Computing match scores...[/bold cyan]\n")

    async def _compute():
        async with AsyncSessionLocal() as db:
            engine = MatchingEngine(db=db)

            try:
                run = await engine.compute_and_cache_matches(
                    buyer_ids=buyer_ids,
                    listing_ids=listing_ids,
                    force_recompute=force,
                )

                console.print(f"[green]✓[/green] Matching run completed (ID: {run.id})")
                console.print(f"  Buyers processed: {run.buyers_processed}")
                console.print(f"  Listings processed: {run.listings_processed}")
                console.print(f"  Matches computed: {run.matches_computed}")

                if run.stats:
                    console.print(f"  Average score: {run.stats.get('avg_score', 0):.1f}")
                    console.print(f"  High-quality matches: {run.stats.get('high_matches', 0)}")

                console.print()

            except Exception as e:
                console.print(f"[red]✗[/red] Error: {str(e)}")
                raise typer.Exit(1)

    asyncio.run(_compute())


@app.command()
def recommend_for_buyer(
    buyer_id: int = typer.Argument(..., help="Buyer (contact) ID"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of recommendations"),
    min_score: Optional[float] = typer.Option(
        None,
        "--min-score",
        "-s",
        help="Minimum match score threshold",
    ),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Don't use cached scores",
    ),
):
    """
    Get listing recommendations for a buyer.

    Example:
        matching-engine recommend-for-buyer 123 --limit 5
    """
    console.print(f"\n[bold cyan]Recommendations for Buyer {buyer_id}[/bold cyan]\n")

    async def _recommend():
        async with AsyncSessionLocal() as db:
            engine = MatchingEngine(db=db)

            try:
                response = await engine.get_recommendations_for_buyer(
                    buyer_id=buyer_id,
                    min_score=min_score,
                    limit=limit,
                    use_cached=not no_cache,
                )

                if not response.recommendations:
                    console.print(f"[yellow]No recommendations found for buyer {buyer_id}[/yellow]")
                    return

                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Rank", style="cyan", width=6)
                table.add_column("Listing ID", style="yellow")
                table.add_column("Listing Name", style="green")
                table.add_column("Score", style="magenta")
                table.add_column("Industry", style="blue")
                table.add_column("Region", style="blue")

                for idx, rec in enumerate(response.recommendations, 1):
                    table.add_row(
                        str(idx),
                        str(rec.listing.id),
                        rec.listing.name[:40],
                        f"{rec.match_score.score:.1f}",
                        rec.listing.industry or "N/A",
                        rec.listing.region or "N/A",
                    )

                console.print(table)
                console.print(
                    f"\nShowing {response.recommendations_count} of "
                    f"{response.total_candidates} candidates"
                )
                console.print(f"Using cached scores: {response.cached}\n")

            except Exception as e:
                console.print(f"[red]✗[/red] Error: {str(e)}")
                raise typer.Exit(1)

    asyncio.run(_recommend())


@app.command()
def recommend_for_listing(
    listing_id: int = typer.Argument(..., help="Listing (deal) ID"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of recommendations"),
    min_score: Optional[float] = typer.Option(
        None,
        "--min-score",
        "-s",
        help="Minimum match score threshold",
    ),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Don't use cached scores",
    ),
):
    """
    Get buyer recommendations for a listing.

    Example:
        matching-engine recommend-for-listing 456 --limit 5
    """
    console.print(f"\n[bold cyan]Recommendations for Listing {listing_id}[/bold cyan]\n")

    async def _recommend():
        async with AsyncSessionLocal() as db:
            engine = MatchingEngine(db=db)

            try:
                response = await engine.get_recommendations_for_listing(
                    listing_id=listing_id,
                    min_score=min_score,
                    limit=limit,
                    use_cached=not no_cache,
                )

                if not response.recommendations:
                    console.print(
                        f"[yellow]No recommendations found for listing {listing_id}[/yellow]"
                    )
                    return

                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Rank", style="cyan", width=6)
                table.add_column("Buyer ID", style="yellow")
                table.add_column("Name", style="green")
                table.add_column("Email", style="green")
                table.add_column("Score", style="magenta")
                table.add_column("Engagement", style="blue")

                for idx, rec in enumerate(response.recommendations, 1):
                    buyer_name = (
                        f"{rec.buyer.first_name or ''} {rec.buyer.last_name or ''}".strip()
                        or "N/A"
                    )
                    table.add_row(
                        str(idx),
                        str(rec.buyer.id),
                        buyer_name[:30],
                        rec.buyer.email or "N/A",
                        f"{rec.match_score.score:.1f}",
                        f"{rec.buyer.engagement_score or 0:.0f}",
                    )

                console.print(table)
                console.print(
                    f"\nShowing {response.recommendations_count} of "
                    f"{response.total_candidates} candidates"
                )
                console.print(f"Using cached scores: {response.cached}\n")

            except Exception as e:
                console.print(f"[red]✗[/red] Error: {str(e)}")
                raise typer.Exit(1)

    asyncio.run(_recommend())


@app.command()
def serve(
    host: str = typer.Option(
        None,
        "--host",
        "-h",
        help="Host to bind (defaults to config)",
    ),
    port: int = typer.Option(
        None,
        "--port",
        "-p",
        help="Port to bind (defaults to config)",
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        "-r",
        help="Enable auto-reload",
    ),
):
    """
    Start the FastAPI server.

    Example:
        matching-engine serve --port 8003 --reload
    """
    import uvicorn

    from app.main import app as fastapi_app

    settings = get_settings()

    uvicorn.run(
        "app.main:app",
        host=host or settings.api_host,
        port=port or settings.api_port,
        reload=reload or settings.api_reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    app()
