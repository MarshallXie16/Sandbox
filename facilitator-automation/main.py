"""
FastAPI application entrypoint for Facilitator Automation.

This is the main API server. Run with:
    uvicorn main:app --host 0.0.0.0 --port 8080 --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import close_db
from app.api import health, engagements, buyers, offers, closings
from app import __version__, __description__


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    setup_logging()
    yield
    # Shutdown
    await close_db()


# Create FastAPI app
app = FastAPI(
    title="Facilitator Automation API",
    description=__description__,
    version=__version__,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods.split(",") if isinstance(settings.cors_allow_methods, str) else ["*"],
    allow_headers=settings.cors_allow_headers.split(",") if isinstance(settings.cors_allow_headers, str) else ["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(engagements.router, prefix="/api/v1")
app.include_router(buyers.router, prefix="/api/v1")
app.include_router(offers.router, prefix="/api/v1")
app.include_router(closings.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Facilitator Automation API",
        "version": __version__,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
