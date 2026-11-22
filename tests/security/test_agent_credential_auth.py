"""Security tests for agent credential authentication and enforcement."""

from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

from app.auth.dependencies import authenticate_agent_credential
from app.common.db import get_engine, get_session_factory
from app.tenants.models import Base


@pytest.fixture(autouse=True)
async def init_db_schema():
    """Ensure schema tables exist in SQLite test memory."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_agent_credential_authentication(client: AsyncClient) -> None:
    # 1. Setup tenant & agent
    t = (await client.post("/api/v1/tenants", json={"name": "Auth Test Corp"})).json()
    headers = {"X-Tenant-ID": t["id"]}

    agent = (
        await client.post(
            "/api/v1/agents",
            json={"name": "AuthAgent", "environment": "production"},
            headers=headers,
        )
    ).json()

    # Issue credential
    cred = (
        await client.post(
            f"/api/v1/agents/{agent['id']}/credentials",
            json={"scopes": ["read"]},
            headers=headers,
        )
    ).json()
    raw_token = cred["raw_token"]

    session_maker = get_session_factory()

    # 2. Valid token authenticates successfully
    async with session_maker() as session:
        auth_agent, auth_cred = await authenticate_agent_credential(
            authorization=f"Bearer {raw_token}", session=session
        )
        assert str(auth_agent.id) == agent["id"]
        assert str(auth_cred.id) == cred["id"]
        assert auth_cred.last_used_at is not None

    # 3. Invalid token fails with 401
    async with session_maker() as session:
        with pytest.raises(Exception) as exc_info:
            await authenticate_agent_credential(
                authorization="Bearer ag_live_invalidtoken1234567890", session=session
            )
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["code"] == "INVALID_TOKEN"

    # 4. Revoked credential fails with 401
    await client.delete(f"/api/v1/agents/{agent['id']}/credentials/{cred['id']}", headers=headers)
    async with session_maker() as session:
        with pytest.raises(Exception) as exc_info:
            await authenticate_agent_credential(
                authorization=f"Bearer {raw_token}", session=session
            )
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["code"] == "AGENT_REVOKED"


@pytest.mark.asyncio
async def test_expired_credential_fails(client: AsyncClient) -> None:
    t = (await client.post("/api/v1/tenants", json={"name": "Expiry Corp"})).json()
    headers = {"X-Tenant-ID": t["id"]}

    agent = (
        await client.post("/api/v1/agents", json={"name": "ExpiringAgent"}, headers=headers)
    ).json()

    expired_time = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
    cred = (
        await client.post(
            f"/api/v1/agents/{agent['id']}/credentials",
            json={"expires_at": expired_time},
            headers=headers,
        )
    ).json()

    session_maker = get_session_factory()
    async with session_maker() as session:
        with pytest.raises(Exception) as exc_info:
            await authenticate_agent_credential(
                authorization=f"Bearer {cred['raw_token']}", session=session
            )
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["code"] == "INVALID_TOKEN"
