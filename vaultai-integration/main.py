"""
VaultAI Integration Layer - Main FastAPI Application
Centralizes AI services for the Capitalink platform.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.database import init_db, close_db
from app.llm.router import llm_router

# API routers
from app.api.health import router as health_router
from app.api.exit_ready_router import router as exit_ready_router
from app.api.facilitator_router import router as facilitator_router
from app.api.crm_router import router as crm_router
from app.api.analytics_router import router as analytics_router

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Handles startup and shutdown tasks:
    - Initialize database
    - Initialize LLM providers
    - Cleanup on shutdown
    """
    # Startup
    logger.info("Starting VaultAI Integration Layer")
    logger.info(f"Environment: {settings.VAULTAI_ENV}")
    logger.info(f"Default LLM provider: {settings.LLM_DEFAULT_PROVIDER}")

    # Initialize database (only in dev)
    if settings.VAULTAI_ENV == "dev":
        await init_db()

    # Log available providers
    logger.info(f"Available LLM providers: {list(llm_router.providers.keys())}")

    yield

    # Shutdown
    logger.info("Shutting down VaultAI Integration Layer")
    await llm_router.close_all()
    await close_db()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="VaultAI Integration Layer",
    description="""
    # VaultAI Integration Layer (Module 10)

    Centralized AI gateway for the Capitalink platform.

    ## Features

    - **Multi-Provider Support**: Connect to local private LLMs or cloud providers
    - **Domain-Specific Services**: Specialized AI services for each module
    - **Security**: PII detection and redaction, API key authentication
    - **Observability**: Request logging, usage tracking, performance metrics

    ## Available Services

    - **Exit Ready**: Investment teasers, checklists, summaries
    - **Facilitator**: Message drafting, negotiation summarization
    - **CRM**: Partner matching, profile enrichment
    - **Analytics**: Insights generation, report creation, metric explanation

    ## Authentication

    All endpoints require an API key via the `X-VaultAI-API-Key` header.
    """,
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.VAULTAI_DEBUG,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(exit_ready_router)
app.include_router(facilitator_router)
app.include_router(crm_router)
app.include_router(analytics_router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.VAULTAI_DEBUG else "An error occurred",
        },
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "VaultAI Integration Layer",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.VAULTAI_ENV,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.VAULTAI_HOST,
        port=settings.VAULTAI_PORT,
        reload=settings.VAULTAI_DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
