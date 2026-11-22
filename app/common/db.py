"""Database connection and session lifecycle."""

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.common.config import get_settings
from app.common.logging import get_logger

logger = get_logger(__name__)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Get or create singleton async database engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        is_sqlite = settings.database_url.startswith("sqlite")
        connect_args = {"check_same_thread": False} if is_sqlite else {}

        engine_kwargs: dict = {
            "echo": settings.debug,
            "connect_args": connect_args,
        }
        if not is_sqlite:
            engine_kwargs.update(
                {
                    "pool_size": settings.database_pool_size,
                    "max_overflow": settings.database_max_overflow,
                    "pool_timeout": settings.database_pool_timeout,
                    "pool_pre_ping": True,
                }
            )

        _engine = create_async_engine(settings.database_url, **engine_kwargs)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create singleton session maker."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _session_factory


async def close_db_engine() -> None:
    """Dispose the database engine and connection pool."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database connection pool closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for yielding database sessions."""
    session_maker = get_session_factory()
    async with session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def check_db_health() -> bool:
    """Execute a simple query to verify database health."""
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error("Database health check failed", error=str(exc))
        return False
