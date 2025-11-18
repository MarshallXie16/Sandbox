"""API v1 router aggregation"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    contacts,
    companies,
    deals,
    activities,
    pipelines,
    associations,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    contacts.router,
    prefix="/contacts",
    tags=["Contacts"],
)

api_router.include_router(
    companies.router,
    prefix="/companies",
    tags=["Companies"],
)

api_router.include_router(
    deals.router,
    prefix="/deals",
    tags=["Deals"],
)

api_router.include_router(
    activities.router,
    prefix="/activities",
    tags=["Activities"],
)

api_router.include_router(
    pipelines.router,
    prefix="/pipelines",
    tags=["Pipelines & Stages"],
)

api_router.include_router(
    associations.router,
    prefix="/associations",
    tags=["Associations"],
)
