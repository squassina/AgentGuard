"""Integration tests verifying PostgreSQL connection, migrations, and queries."""

import uuid

import pytest
from sqlalchemy import text

from app.common.config import get_settings
from app.common.db import check_db_health, close_db_engine, get_session_factory


@pytest.mark.asyncio
async def test_postgres_live_connection_and_tenants_table() -> None:
    """Verify live PostgreSQL connectivity and schema if DATABASE_URL points to postgres."""
    settings = get_settings()
    if not settings.database_url.startswith("postgresql"):
        pytest.skip("Not configured for PostgreSQL")

    try:
        assert await check_db_health() is True

        session_maker = get_session_factory()
        tenant_id = uuid.uuid4()
        tenant_name = f"tenant-{uuid.uuid4().hex[:8]}"

        async with session_maker() as session:
            # Insert test tenant
            await session.execute(
                text("INSERT INTO tenants (id, name, status) VALUES (:id, :name, :status)"),
                {"id": tenant_id, "name": tenant_name, "status": "active"},
            )
            await session.commit()

        async with session_maker() as session:
            # Query tenant back
            result = await session.execute(
                text("SELECT id, name, status FROM tenants WHERE id = :id"),
                {"id": tenant_id},
            )
            row = result.fetchone()
            assert row is not None
            assert row[0] == tenant_id
            assert row[1] == tenant_name
            assert row[2] == "active"

            # Insert test agent in PostgreSQL
            agent_id = uuid.uuid4()
            await session.execute(
                text(
                    "INSERT INTO agents (id, tenant_id, name, environment, status, metadata_json) "
                    "VALUES (:id, :tenant_id, :name, :env, :status, :meta)"
                ),
                {
                    "id": agent_id,
                    "tenant_id": tenant_id,
                    "name": "pg-agent",
                    "env": "development",
                    "status": "active",
                    "meta": "{}",
                },
            )
            await session.commit()

            # Verify agent in PostgreSQL
            agent_res = await session.execute(
                text("SELECT id, name FROM agents WHERE id = :id"),
                {"id": agent_id},
            )
            agent_row = agent_res.fetchone()
            assert agent_row is not None
            assert agent_row[1] == "pg-agent"

            # Cleanup
            await session.execute(
                text("DELETE FROM tenants WHERE id = :id"),
                {"id": tenant_id},
            )
            await session.commit()
    finally:
        await close_db_engine()
