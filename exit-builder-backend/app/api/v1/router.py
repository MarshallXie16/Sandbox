"""
API v1 router - combines all v1 routes
"""
from fastapi import APIRouter

from app.api.v1.routes import quick

api_router = APIRouter()

# Include route modules
api_router.include_router(quick.router)
