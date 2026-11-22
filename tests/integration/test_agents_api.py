"""Integration tests for Tenant and Agent CRUD API."""

import pytest
from httpx import AsyncClient

from app.common.db import get_engine
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
async def test_agent_lifecycle_and_credentials(client: AsyncClient) -> None:
    # 1. Create Tenant
    t_res = await client.post("/api/v1/tenants", json={"name": "Acme Corp"})
    assert t_res.status_code == 201
    tenant_id = t_res.json()["id"]

    headers = {"X-Tenant-ID": tenant_id}

    # 2. Register Agent
    agent_payload = {
        "name": "CustomerSupportBot",
        "environment": "development",
        "metadata": {"version": "1.0", "team": "support"},
    }
    a_res = await client.post("/api/v1/agents", json=agent_payload, headers=headers)
    assert a_res.status_code == 201
    agent = a_res.json()
    agent_id = agent["id"]
    assert agent["name"] == "CustomerSupportBot"
    assert agent["tenant_id"] == tenant_id
    assert agent["status"] == "active"
    assert agent["metadata"]["team"] == "support"

    # 3. Get Agent
    get_res = await client.get(f"/api/v1/agents/{agent_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == agent_id

    # 4. List Agents
    list_res = await client.get("/api/v1/agents", headers=headers)
    assert list_res.status_code == 200
    agents = list_res.json()
    assert len(agents) == 1
    assert agents[0]["id"] == agent_id

    # 5. Issue Credential
    c_res = await client.post(
        f"/api/v1/agents/{agent_id}/credentials",
        json={"scopes": ["mcp:read", "mcp:call"]},
        headers=headers,
    )
    assert c_res.status_code == 201
    cred = c_res.json()
    assert "raw_token" in cred
    assert cred["raw_token"].startswith("ag_dev_")
    cred_id = cred["id"]
    raw_token = cred["raw_token"]

    # 6. List Credentials (verify raw_token is NOT exposed)
    list_creds_res = await client.get(f"/api/v1/agents/{agent_id}/credentials", headers=headers)
    assert list_creds_res.status_code == 200
    creds_list = list_creds_res.json()
    assert len(creds_list) == 1
    assert "raw_token" not in creds_list[0]
    assert creds_list[0]["id"] == cred_id

    # 7. Rotate Credential
    rot_res = await client.post(
        f"/api/v1/agents/{agent_id}/credentials/{cred_id}/rotate",
        headers=headers,
    )
    assert rot_res.status_code == 200
    rot_cred = rot_res.json()
    assert "raw_token" in rot_cred
    assert rot_cred["id"] != cred_id
    assert rot_cred["raw_token"] != raw_token

    # Verify old credential is now revoked
    creds_after_rot = (
        await client.get(f"/api/v1/agents/{agent_id}/credentials", headers=headers)
    ).json()
    assert len(creds_after_rot) == 2
    old_cred = next(c for c in creds_after_rot if c["id"] == cred_id)
    assert old_cred["revoked_at"] is not None

    # 8. Revoke Agent completely
    rev_res = await client.post(f"/api/v1/agents/{agent_id}/revoke", headers=headers)
    assert rev_res.status_code == 200
    assert rev_res.json()["status"] == "revoked"

    # Verify all credentials now revoked
    final_creds = (
        await client.get(f"/api/v1/agents/{agent_id}/credentials", headers=headers)
    ).json()
    assert all(c["revoked_at"] is not None for c in final_creds)
