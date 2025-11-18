"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import init_db, logger, settings
from app.api.routes import router

# Create FastAPI app
app = FastAPI(
    title="Indie Engagement Tracker",
    description="Client Engagement Tracker for IndieStack CRM and Capital Ink Hub",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize application on startup."""
    logger.info("Starting Indie Engagement Tracker API...")
    logger.info(f"Environment: {settings.app_env}")

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    logger.info("Shutting down Indie Engagement Tracker API...")


@app.get("/")
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "service": "Indie Engagement Tracker",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
