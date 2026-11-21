"""Integration tests for database health check."""

import pytest

from app.common.db import check_db_health, close_db_engine


@pytest.mark.asyncio
async def test_database_health_check_memory_sqlite() -> None:
    """Verify check_db_health succeeds with SQLite in test environment."""
    try:
        healthy = await check_db_health()
        assert healthy is True
    finally:
        await close_db_engine()
