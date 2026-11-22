"""FastAPI application entrypoint and lifecycle."""

import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import RequestResponseEndpoint

from app.api.router import api_router
from app.api.routes.health import router as health_router
from app.common.config import get_settings
from app.common.db import close_db_engine, get_engine
from app.common.logging import configure_logging, correlation_id_ctx, get_logger

logger = get_logger("agentguard.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for startup and shutdown."""
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("AgentGuard starting up", environment=settings.environment)

    # Initialize DB engine
    get_engine()

    yield

    logger.info("AgentGuard shutting down")
    await close_db_engine()


def create_app() -> FastAPI:
    """Application factory for AgentGuard."""
    settings = get_settings()
    app = FastAPI(
        title="AgentGuard",
        description="Cloud-hosted MCP Security Gateway and Control Plane",
        version="0.1.0",
        lifespan=lifespan,
        debug=settings.debug,
    )

    @app.middleware("http")
    async def correlation_id_middleware(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Inject or propagate X-Request-ID correlation header."""
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.state.request_id = request_id
        token = correlation_id_ctx.set(request_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            correlation_id_ctx.reset(token)

    # Include routers
    app.include_router(health_router)
    app.include_router(api_router)

    return app


app = create_app()
