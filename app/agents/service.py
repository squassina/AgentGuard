"""Domain services for managing agents and their credentials."""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.models import Agent, AgentCredential
from app.agents.schemas import AgentCreate, AgentUpdate, CredentialCreate
from app.auth.security import generate_agent_token


class AgentService:
    """Service handling Agent and Credential lifecycle scoped strictly to a tenant."""

    @staticmethod
    async def create_agent(
        session: AsyncSession,
        tenant_id: uuid.UUID,
        data: AgentCreate,
        owner_user_id: uuid.UUID | None = None,
    ) -> Agent:
        # Check name uniqueness within tenant
        existing = await session.execute(
            select(Agent).where(Agent.tenant_id == tenant_id, Agent.name == data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "AGENT_NAME_EXISTS",
                    "message": f"Agent named '{data.name}' already exists",
                },
            )

        agent = Agent(
            tenant_id=tenant_id,
            name=data.name,
            environment=data.environment,
            metadata_json=data.metadata,
            owner_user_id=owner_user_id,
            status="active",
        )
        session.add(agent)
        await session.commit()
        await session.refresh(agent)
        return agent

    @staticmethod
    async def get_agent(session: AsyncSession, tenant_id: uuid.UUID, agent_id: uuid.UUID) -> Agent:
        result = await session.execute(
            select(Agent).where(Agent.id == agent_id, Agent.tenant_id == tenant_id)
        )
        agent = result.scalar_one_or_none()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "AGENT_NOT_FOUND", "message": "Agent not found"},
            )
        return agent

    @staticmethod
    async def list_agents(
        session: AsyncSession,
        tenant_id: uuid.UUID,
        environment: str | None = None,
        status_filter: str | None = None,
    ) -> list[Agent]:
        stmt = select(Agent).where(Agent.tenant_id == tenant_id)
        if environment:
            stmt = stmt.where(Agent.environment == environment)
        if status_filter:
            stmt = stmt.where(Agent.status == status_filter)
        stmt = stmt.order_by(Agent.created_at.desc())
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_agent(
        session: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        data: AgentUpdate,
    ) -> Agent:
        agent = await AgentService.get_agent(session, tenant_id, agent_id)
        if data.name is not None and data.name != agent.name:
            # Check unique name within tenant
            existing = await session.execute(
                select(Agent).where(Agent.tenant_id == tenant_id, Agent.name == data.name)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "AGENT_NAME_EXISTS",
                        "message": f"Agent named '{data.name}' already exists",
                    },
                )
            agent.name = data.name

        if data.environment is not None:
            agent.environment = data.environment
        if data.status is not None:
            agent.status = data.status
        if data.metadata is not None:
            agent.metadata_json = data.metadata

        agent.updated_at = datetime.now(UTC)
        await session.commit()
        await session.refresh(agent)
        return agent

    @staticmethod
    async def issue_credential(
        session: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        data: CredentialCreate,
    ) -> tuple[AgentCredential, str]:
        agent = await AgentService.get_agent(session, tenant_id, agent_id)
        if agent.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "AGENT_NOT_ACTIVE",
                    "message": f"Cannot issue credentials for {agent.status} agent",
                },
            )

        raw_token, prefix, token_hash = generate_agent_token(agent.environment)
        credential = AgentCredential(
            tenant_id=tenant_id,
            agent_id=agent.id,
            credential_prefix=prefix,
            credential_hash=token_hash,
            scopes=data.scopes,
            expires_at=data.expires_at,
        )
        session.add(credential)
        await session.commit()
        await session.refresh(credential)
        return credential, raw_token

    @staticmethod
    async def list_credentials(
        session: AsyncSession, tenant_id: uuid.UUID, agent_id: uuid.UUID
    ) -> list[AgentCredential]:
        await AgentService.get_agent(session, tenant_id, agent_id)
        result = await session.execute(
            select(AgentCredential)
            .where(AgentCredential.tenant_id == tenant_id, AgentCredential.agent_id == agent_id)
            .order_by(AgentCredential.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def revoke_credential(
        session: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        credential_id: uuid.UUID,
    ) -> AgentCredential:
        await AgentService.get_agent(session, tenant_id, agent_id)
        result = await session.execute(
            select(AgentCredential).where(
                AgentCredential.id == credential_id,
                AgentCredential.agent_id == agent_id,
                AgentCredential.tenant_id == tenant_id,
            )
        )
        cred = result.scalar_one_or_none()
        if not cred:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "CREDENTIAL_NOT_FOUND", "message": "Credential not found"},
            )
        if cred.revoked_at is None:
            cred.revoked_at = datetime.now(UTC)
            await session.commit()
            await session.refresh(cred)
        return cred

    @staticmethod
    async def rotate_credential(
        session: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        credential_id: uuid.UUID,
    ) -> tuple[AgentCredential, str]:
        # Revoke old credential
        old_cred = await AgentService.revoke_credential(session, tenant_id, agent_id, credential_id)
        # Issue new credential preserving scopes
        new_cred, raw_token = await AgentService.issue_credential(
            session,
            tenant_id,
            agent_id,
            CredentialCreate(scopes=old_cred.scopes, expires_at=old_cred.expires_at),
        )
        return new_cred, raw_token

    @staticmethod
    async def revoke_agent(
        session: AsyncSession, tenant_id: uuid.UUID, agent_id: uuid.UUID
    ) -> Agent:
        agent = await AgentService.get_agent(session, tenant_id, agent_id)
        agent.status = "revoked"
        agent.updated_at = datetime.now(UTC)

        # Revoke all active credentials for this agent
        creds_res = await session.execute(
            select(AgentCredential).where(
                AgentCredential.tenant_id == tenant_id,
                AgentCredential.agent_id == agent_id,
                AgentCredential.revoked_at.is_(None),
            )
        )
        now = datetime.now(UTC)
        for cred in creds_res.scalars().all():
            cred.revoked_at = now

        await session.commit()
        await session.refresh(agent)
        return agent
