"""Unit tests for health endpoints and correlation ID middleware."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_live(client: AsyncClient) -> None:
    """Verify liveness probe returns 200 OK."""
    response = await client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_health_ready_success(client: AsyncClient) -> None:
    """Verify readiness probe returns 200 when database check succeeds."""
    with patch("app.api.routes.health.check_db_health", new_callable=AsyncMock) as mock_check:
        mock_check.return_value = True
        response = await client.get("/health/ready")
        assert response.status_code == 200
        assert response.json() == {"status": "ready", "database": "connected"}


@pytest.mark.asyncio
async def test_health_ready_failure(client: AsyncClient) -> None:
    """Verify readiness probe returns 503 when database check fails."""
    with patch("app.api.routes.health.check_db_health", new_callable=AsyncMock) as mock_check:
        mock_check.return_value = False
        response = await client.get("/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["detail"]["status"] == "not_ready"


@pytest.mark.asyncio
async def test_correlation_id_propagated(client: AsyncClient) -> None:
    """Verify client-supplied X-Request-ID is preserved."""
    custom_id = "test-custom-req-id-999"
    response = await client.get("/health/live", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_id
