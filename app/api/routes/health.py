"""Health and readiness endpoints."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.common.db import check_db_health

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    status: str


class ReadinessResponse(BaseModel):
    status: str
    database: str


@router.get("/health/live", response_model=HealthResponse)
async def health_live() -> HealthResponse:
    """Liveness probe indicating process is responsive."""
    return HealthResponse(status="ok")


@router.get("/health/ready", response_model=ReadinessResponse)
async def health_ready() -> ReadinessResponse:
    """Readiness probe checking critical dependencies like PostgreSQL."""
    is_ready = await check_db_health()
    if not is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "database": "disconnected"},
        )
    return ReadinessResponse(status="ready", database="connected")


@router.get("/metrics")
async def metrics() -> dict[str, str]:
    """Basic metrics probe endpoint."""
    return {"status": "ok"}
