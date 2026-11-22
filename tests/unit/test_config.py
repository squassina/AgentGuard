"""Unit tests for configuration validation."""

from app.common.config import Settings


def test_default_settings() -> None:
    """Verify default settings instantiation."""
    settings = Settings()
    assert settings.app_port == 8000
    assert settings.log_level in ["INFO", "DEBUG"]
    assert settings.database_pool_size == 10
    assert len(settings.secret_key) >= 32


def test_override_settings(monkeypatch) -> None:
    """Verify settings override via environment variables."""
    monkeypatch.setenv("APP_PORT", "9000")
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings()
    assert settings.app_port == 9000
    assert settings.environment == "staging"
    assert settings.log_level == "DEBUG"
