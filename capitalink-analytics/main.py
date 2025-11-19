"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import __version__
from app.api import crm, exit_ready, facilitator, health
from app.core.config import settings
from app.core.database import db_manager
from app.core.logging import setup_logging
from app.ui import dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging()
    await db_manager.initialize()
    yield
    # Shutdown
    await db_manager.close()


# Create FastAPI app
app = FastAPI(
    title="Capitalink Analytics",
    description="Read-only analytics and reporting service for Capitalink platform",
    version=__version__,
    lifespan=lifespan,
)

# CORS
if settings.get_cors_origins():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

# API routes
app.include_router(health.router, prefix="/api/v1")
app.include_router(exit_ready.router, prefix="/api/v1/analytics")
app.include_router(facilitator.router, prefix="/api/v1/analytics")
app.include_router(crm.router, prefix="/api/v1/analytics")

# Dashboard routes
app.include_router(dashboard.router)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - redirect to dashboard."""
    return """
    <html>
        <head>
            <title>Capitalink Analytics</title>
            <meta http-equiv="refresh" content="0; url=/dashboard" />
        </head>
        <body>
            <p>Redirecting to <a href="/dashboard">dashboard</a>...</p>
        </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.analytics_host,
        port=settings.analytics_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
