"""Security tests verifying multi-tenant isolation and non-disclosing 404s."""

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
async def test_tenant_isolation_cross_tenant_access_denied(client: AsyncClient) -> None:
    # 1. Create Tenant A and Tenant B
    t_a = (await client.post("/api/v1/tenants", json={"name": "Tenant Alpha"})).json()
    t_b = (await client.post("/api/v1/tenants", json={"name": "Tenant Beta"})).json()

    headers_a = {"X-Tenant-ID": t_a["id"]}
    headers_b = {"X-Tenant-ID": t_b["id"]}

    # 2. Tenant A creates Agent A
    agent_a = (
        await client.post(
            "/api/v1/agents",
            json={"name": "Agent A", "environment": "production"},
            headers=headers_a,
        )
    ).json()

    # 3. Tenant B tries to get Agent A -> must return 404 (non-disclosing)
    res_get = await client.get(f"/api/v1/agents/{agent_a['id']}", headers=headers_b)
    assert res_get.status_code == 404
    assert res_get.json()["detail"]["code"] == "AGENT_NOT_FOUND"

    # 4. Tenant B tries to update Agent A -> 404
    res_patch = await client.patch(
        f"/api/v1/agents/{agent_a['id']}", json={"name": "Hacked Name"}, headers=headers_b
    )
    assert res_patch.status_code == 404

    # 5. Tenant B tries to issue credentials for Agent A -> 404
    res_cred = await client.post(
        f"/api/v1/agents/{agent_a['id']}/credentials",
        json={"scopes": ["mcp:admin"]},
        headers=headers_b,
    )
    assert res_cred.status_code == 404

    # 6. Tenant B tries to revoke Agent A -> 404
    res_rev = await client.post(f"/api/v1/agents/{agent_a['id']}/revoke", headers=headers_b)
    assert res_rev.status_code == 404

    # 7. Same agent name in different tenants is allowed (tenant-scoped namespace)
    res_same_name = await client.post(
        "/api/v1/agents",
        json={"name": "Agent A", "environment": "development"},
        headers=headers_b,
    )
    assert res_same_name.status_code == 201
    assert res_same_name.json()["id"] != agent_a["id"]
