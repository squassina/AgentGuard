"""Application configuration and validation."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """AgentGuard configuration settings loaded from environment."""

    environment: str = Field(default="development", description="Runtime environment")
    debug: bool = Field(default=False, description="Debug mode")
    app_host: str = Field(default="0.0.0.0", description="Application bind host")
    app_port: int = Field(default=8000, description="Application bind port")
    log_level: str = Field(default="INFO", description="Log level")

    # PostgreSQL
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/agentguard",
        description="Async PostgreSQL connection string",
    )
    database_pool_size: int = Field(default=10, description="Connection pool size")
    database_max_overflow: int = Field(default=20, description="Maximum overflow connections")
    database_pool_timeout: int = Field(default=30, description="Connection pool timeout in seconds")

    # Security
    secret_key: str = Field(
        default="change-me-to-a-secure-random-string-at-least-32-chars-long",
        description="Secret key for application cryptography",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
