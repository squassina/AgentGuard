"""Root API v1 router definition."""

from fastapi import APIRouter

from app.api.routes.agents import router as agents_router
from app.api.routes.tenants import router as tenants_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(tenants_router)
api_router.include_router(agents_router)
