"""
Main FastAPI application entrypoint.

Capital Ink Hub Portal API
Backend API for WordPress member portal integration.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.database import init_db, close_db
from app.api import health, members, listings, interests, recommendations, resources

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Portal API")
    logger.info(f"Environment: {settings.PORTAL_ENV}")
    logger.info(f"Version: {settings.PORTAL_VERSION}")

    await init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down Portal API")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="Capital Ink Hub Portal API",
    description="Backend API for WordPress member portal integration with IndieStack CRM",
    version=settings.PORTAL_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

# Add CORS middleware if configured
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS enabled for origins: {settings.get_cors_origins()}")

# Include routers
# Health check (no /api/v1 prefix, no auth required)
app.include_router(health.router, prefix="/api/v1")

# API v1 routers (all require authentication)
app.include_router(members.router, prefix="/api/v1")
app.include_router(listings.router, prefix="/api/v1")
app.include_router(interests.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(resources.router, prefix="/api/v1")

logger.info("All routers registered")


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint redirect."""
    return {
        "name": "Capital Ink Hub Portal API",
        "version": settings.PORTAL_VERSION,
        "docs": "/docs" if settings.is_development else "disabled",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )
