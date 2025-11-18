"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db, close_db
from app.api.v1 import auth, users, profiles, matching, partnerships

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,  # Disable docs in production
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
    """Initialize database on startup."""
    # await init_db()  # Uncomment after migrations are set up
    pass


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    await close_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to GrowthPact API",
        "version": settings.API_VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers
app.include_router(auth.router, prefix=f"/api/{settings.API_VERSION}", tags=["Authentication"])
app.include_router(users.router, prefix=f"/api/{settings.API_VERSION}", tags=["Users"])
app.include_router(profiles.router, prefix=f"/api/{settings.API_VERSION}", tags=["Profiles"])
app.include_router(matching.router, prefix=f"/api/{settings.API_VERSION}", tags=["Matching"])
app.include_router(partnerships.router, prefix=f"/api/{settings.API_VERSION}", tags=["Partnerships"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
