"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.v1.router import api_router

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Capital Link Exit Builder - Business Valuation API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint

    Returns:
        dict: Status and version information
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint - API information

    Returns:
        dict: Welcome message and API details
    """
    return {
        "message": "Welcome to Capital Link Exit Builder API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
