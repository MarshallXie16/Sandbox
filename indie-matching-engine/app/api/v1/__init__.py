"""
API v1 routes.
"""

from fastapi import APIRouter

from app.api.v1 import matches, recommendations

api_router = APIRouter()

api_router.include_router(
    recommendations.router,
    prefix="/recommendations",
    tags=["recommendations"],
)

api_router.include_router(
    matches.router,
    prefix="/matches",
    tags=["matches"],
)
