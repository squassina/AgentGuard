"""Tenant management API endpoints."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.db import get_db
from app.tenants.models import Tenant

router = APIRouter(prefix="/tenants", tags=["tenants"])


class TenantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class TenantResponse(BaseModel):
    id: uuid.UUID
    name: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    data: TenantCreate,
    session: AsyncSession = Depends(get_db),
) -> TenantResponse:
    """Provision a new tenant."""
    existing = await session.execute(select(Tenant).where(Tenant.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "TENANT_EXISTS", "message": f"Tenant '{data.name}' already exists"},
        )
    tenant = Tenant(name=data.name, status="active")
    session.add(tenant)
    await session.commit()
    await session.refresh(tenant)
    return TenantResponse.model_validate(tenant)


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> TenantResponse:
    """Get tenant by ID."""
    tenant = await session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TENANT_NOT_FOUND", "message": "Tenant not found"},
        )
    return TenantResponse.model_validate(tenant)
