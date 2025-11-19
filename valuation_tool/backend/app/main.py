"""Main FastAPI application for Exit Builder."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import close_db

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    pass


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    await close_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Exit Builder API",
        "version": settings.API_VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and include routers
from app.api.v1 import projects, financials, valuations, dcf, reports

app.include_router(projects.router, prefix=f"/api/{settings.API_VERSION}", tags=["Projects"])
app.include_router(financials.router, prefix=f"/api/{settings.API_VERSION}", tags=["Financials"])
app.include_router(valuations.router, prefix=f"/api/{settings.API_VERSION}", tags=["Valuations"])
app.include_router(dcf.router, prefix=f"/api/{settings.API_VERSION}", tags=["DCF"])
app.include_router(reports.router, prefix=f"/api/{settings.API_VERSION}", tags=["Reports"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
