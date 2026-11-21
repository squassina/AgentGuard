"""Pytest configuration and fixtures."""

import os

import pytest
from httpx import ASGITransport, AsyncClient

from app.common.config import get_settings
from app.main import create_app


@pytest.fixture(autouse=True)
def test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set default test environment variables."""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DEBUG", "true")
    if "DATABASE_URL" not in os.environ:
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    get_settings.cache_clear()


@pytest.fixture
def app():
    """Create and return application instance for testing."""
    return create_app()


@pytest.fixture
async def client(app) -> AsyncClient:
    """Provide an async test client."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        yield ac
