"""Agent management API endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.schemas import (
    AgentCreate,
    AgentResponse,
    AgentUpdate,
    CredentialCreate,
    CredentialIssuedResponse,
    CredentialResponse,
)
from app.agents.service import AgentService
from app.auth.dependencies import AuthenticatedActor, get_current_actor
from app.common.db import get_db

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    data: AgentCreate,
    actor: AuthenticatedActor = Depends(get_current_actor),
    session: AsyncSession = Depends(get_db),
) -> AgentResponse:
    """Register a new agent scoped to the caller's tenant."""
    agent = await AgentService.create_agent(session, actor.tenant_id, data, actor.user_id)
    return AgentResponse.model_validate(agent)


@router.get("", response_model=list[AgentResponse])
async def list_agents(
    environment: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    actor: AuthenticatedActor = Depends(get_current_actor),
    session: AsyncSession = Depends(get_db),
) -> list[AgentResponse]:
    """List all agents for the current tenant."""
    agents = await AgentService.list_agents(session, actor.tenant_id, environment, status_filter)
    return [AgentResponse.model_validate(a) for a in agents]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: uuid.UUID,
    actor: AuthenticatedActor = Depends(get_current_actor),
    session: AsyncSession = Depends(get_db),
) -> AgentResponse:
    """Get single agent details by ID within current tenant."""
    agent = await AgentService.get_agent(session, actor.tenant_id, agent_id)
    return AgentResponse.model_validate(agent)


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: uuid.UUID,
    data: AgentUpdate,
    actor: AuthenticatedActor = Depends(get_current_actor),
    session: AsyncSession = Depends(get_db),
) -> AgentResponse:
    """Update agent metadata, environment, or status."""
    agent = await AgentService.update_agent(session, actor.tenant_id, agent_id, data)
    return AgentResponse.model_validate(agent)


@router.post(
    "/{agent_id}/credentials",
    response_model=CredentialIssuedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def issue_credential(
    agent_id: uuid.UUID,
    data: CredentialCreate,
    actor: AuthenticatedActor = Depends(get_current_actor),
    session: AsyncSession = Depends(get_db),
) -> CredentialIssuedResponse:
    """Issue a new credential for an agent. Raw token is displayed once."""
    credential, raw_token = await AgentService.issue_credential(
        session, actor.tenant_id, agent_id, data
    )
    return CredentialIssuedResponse(
        id=credential.id,
        agent_id=credential.agent_id,
        tenant_id=credential.tenant_id,
        credential_prefix=credential.credential_prefix,
        raw_token=raw_token,
        scopes=credential.scopes,
        expires_at=credential.expires_at,
        created_at=credential.created_at,
    )


@router.get("/{agent_id}/credentials", response_model=list[CredentialResponse])
async def list_credentials(
    agent_id: uuid.UUID,
    actor: AuthenticatedActor = Depends(get_current_actor),
    session: AsyncSession = Depends(get_db),
) -> list[CredentialResponse]:
    """List credential metadata (without raw tokens) for an agent."""
    creds = await AgentService.list_credentials(session, actor.tenant_id, agent_id)
    return [CredentialResponse.model_validate(c) for c in creds]


@router.post(
    "/{agent_id}/credentials/{credential_id}/rotate",
    response_model=CredentialIssuedResponse,
)
async def rotate_credential(
    agent_id: uuid.UUID,
    credential_id: uuid.UUID,
    actor: AuthenticatedActor = Depends(get_current_actor),
    session: AsyncSession = Depends(get_db),
) -> CredentialIssuedResponse:
    """Rotate credential: atomically revokes old credential and issues a replacement."""
    new_cred, raw_token = await AgentService.rotate_credential(
        session, actor.tenant_id, agent_id, credential_id
    )
    return CredentialIssuedResponse(
        id=new_cred.id,
        agent_id=new_cred.agent_id,
        tenant_id=new_cred.tenant_id,
        credential_prefix=new_cred.credential_prefix,
        raw_token=raw_token,
        scopes=new_cred.scopes,
        expires_at=new_cred.expires_at,
        created_at=new_cred.created_at,
    )


@router.delete("/{agent_id}/credentials/{credential_id}", response_model=CredentialResponse)
async def revoke_credential(
    agent_id: uuid.UUID,
    credential_id: uuid.UUID,
    actor: AuthenticatedActor = Depends(get_current_actor),
    session: AsyncSession = Depends(get_db),
) -> CredentialResponse:
    """Revoke an agent credential immediately."""
    cred = await AgentService.revoke_credential(session, actor.tenant_id, agent_id, credential_id)
    return CredentialResponse.model_validate(cred)


@router.post("/{agent_id}/revoke", response_model=AgentResponse)
async def revoke_agent(
    agent_id: uuid.UUID,
    actor: AuthenticatedActor = Depends(get_current_actor),
    session: AsyncSession = Depends(get_db),
) -> AgentResponse:
    """Revoke an agent completely and revoke all its active credentials."""
    agent = await AgentService.revoke_agent(session, actor.tenant_id, agent_id)
    return AgentResponse.model_validate(agent)
