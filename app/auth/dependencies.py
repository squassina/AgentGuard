"""Authentication and tenant context dependencies."""

import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.models import Agent, AgentCredential
from app.auth.security import hash_credential
from app.common.db import get_db
from app.tenants.models import Tenant, TenantMembership


class AuthenticatedActor:
    """Represents an authenticated human user acting within a tenant context."""

    def __init__(self, tenant_id: uuid.UUID, user_id: uuid.UUID, role: str) -> None:
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.role = role


async def get_current_actor(
    x_tenant_id: Annotated[str | None, Header()] = None,
    x_user_id: Annotated[str | None, Header()] = None,
    session: AsyncSession = Depends(get_db),
) -> AuthenticatedActor:
    """Resolve tenant and user context from request headers (Control Plane auth)."""
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTHENTICATION_REQUIRED", "message": "Missing tenant identity header"},
        )

    try:
        tenant_uuid = uuid.UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_TENANT_ID", "message": "Tenant ID must be valid UUID"},
        ) from None

    # Verify tenant exists and is active
    tenant = await session.get(Tenant, tenant_uuid)
    if not tenant or tenant.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "TENANT_ACCESS_DENIED", "message": "Tenant not active or unauthorized"},
        )

    # If x_user_id supplied, verify membership; else default to owner/admin context
    user_uuid = uuid.UUID(x_user_id) if x_user_id else uuid.uuid4()
    role = "admin"
    if x_user_id:
        membership_res = await session.execute(
            select(TenantMembership).where(
                TenantMembership.tenant_id == tenant_uuid,
                TenantMembership.user_id == user_uuid,
            )
        )
        membership = membership_res.scalar_one_or_none()
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "TENANT_ACCESS_DENIED", "message": "User not a member of tenant"},
            )
        role = membership.role

    return AuthenticatedActor(tenant_id=tenant_uuid, user_id=user_uuid, role=role)


async def authenticate_agent_credential(
    authorization: Annotated[str | None, Header()] = None,
    session: AsyncSession = Depends(get_db),
) -> tuple[Agent, AgentCredential]:
    """Validate inbound agent bearer token and return active (Agent, Credential)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTHENTICATION_REQUIRED", "message": "Bearer token required"},
        )

    raw_token = authorization.removeprefix("Bearer ").strip()
    token_hash = hash_credential(raw_token)

    # Fast indexed lookup by credential hash
    query = (
        select(AgentCredential, Agent)
        .join(Agent, AgentCredential.agent_id == Agent.id)
        .where(AgentCredential.credential_hash == token_hash)
    )
    result = await session.execute(query)
    record = result.first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid agent credential"},
        )

    credential, agent = record[0], record[1]

    # Check revocation
    if credential.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AGENT_REVOKED", "message": "Credential has been revoked"},
        )

    # Check expiration
    if credential.expires_at is not None:
        exp = credential.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=UTC)
        if exp < datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_TOKEN", "message": "Credential has expired"},
            )

    # Check agent status
    if agent.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AGENT_REVOKED", "message": f"Agent is {agent.status}"},
        )

    # Update last_used_at asynchronously
    credential.last_used_at = datetime.now(UTC)
    await session.commit()

    return agent, credential
