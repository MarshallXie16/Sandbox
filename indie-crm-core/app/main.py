"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    IndieStack CRM - A HubSpot-inspired CRM system for managing contacts, companies, deals, and activities.

    ## Features

    - **Contacts**: Manage contacts with customizable categories (sellers, buyers, bankers, etc.)
    - **Companies**: Track companies with business metrics and custom fields
    - **Deals**: Manage sales opportunities through customizable pipelines
    - **Activities**: Log all interactions (emails, calls, meetings, social)
    - **Pipelines & Stages**: Configurable deal pipelines stored in database
    - **Associations**: Link entities together (HubSpot-style associations)
    - **Extensible**: All entities support custom fields via JSONB details

    ## Data Model

    All main entities (Contacts, Companies, Deals, Activities) include a `details` JSON field
    for storing custom attributes without schema changes. This allows for:
    - Category-specific fields (seller vs. buyer contact attributes)
    - Integration metadata (external system IDs)
    - Future custom fields added by users

    ## Associations

    Entities can be linked using association endpoints:
    - Contacts ↔ Companies (with role)
    - Contacts ↔ Deals (with role)
    - Companies ↔ Deals (with role)
    - Activities ↔ Contacts, Companies, Deals

    This mirrors HubSpot's association model for flexible relationship tracking.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to IndieStack CRM API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.APP_VERSION}
