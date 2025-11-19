"""
VaultAI Integration Layer - Provider CLI Commands
"""

import asyncio
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


@app.command()
def list():
    """List all configured LLM providers."""
    from app.llm.router import llm_router

    table = Table(title="LLM Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Base URL", style="yellow")
    table.add_column("Model", style="green")
    table.add_column("Status", style="magenta")

    for provider_name, client in llm_router.providers.items():
        table.add_row(
            provider_name,
            client.config.base_url,
            client.config.model,
            "✓ Active",
        )

    console.print(table)


@app.command()
def test(provider: str = typer.Argument(..., help="Provider name to test")):
    """Test connection to an LLM provider."""
    from app.llm.router import llm_router
    from app.schemas.llm import ChatMessage, LLMRequest

    async def run():
        if provider not in llm_router.providers:
            console.print(f"[red]Provider '{provider}' not found[/red]")
            return

        console.print(f"[cyan]Testing provider: {provider}[/cyan]")

        # Simple test request
        test_request = LLMRequest(
            messages=[
                ChatMessage(role="system", content="You are a helpful assistant."),
                ChatMessage(role="user", content="Say hello!"),
            ],
            max_tokens=50,
        )

        try:
            response = await llm_router.chat(
                request=test_request,
                provider_override=provider,
            )
            console.print(f"[green]✓ Success![/green]")
            console.print(f"Response: {response.content}")
            console.print(f"Tokens: {response.usage.total_tokens if response.usage else 'N/A'}")
            console.print(f"Latency: {response.latency_ms:.0f}ms")
        except Exception as e:
            console.print(f"[red]✗ Failed: {e}[/red]")

    asyncio.run(run())
