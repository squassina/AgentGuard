"""Structured logging setup with correlation IDs and secret redaction."""

import contextvars
import logging
import sys
from typing import Any

import structlog

# Context variable for request correlation ID
correlation_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "correlation_id", default=None
)

REDACTED_KEYS = {
    "authorization",
    "proxy-authorization",
    "cookie",
    "set-cookie",
    "secret",
    "secret_key",
    "token",
    "access_token",
    "refresh_token",
    "password",
    "credential",
    "api_key",
    "apikey",
}


def add_correlation_id(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Inject request correlation ID into log event if present."""
    cid = correlation_id_ctx.get()
    if cid:
        event_dict["request_id"] = cid
    return event_dict


def redact_sensitive_data(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Recursively redact sensitive fields from structured log records."""
    for key, value in list(event_dict.items()):
        if str(key).lower() in REDACTED_KEYS:
            event_dict[key] = "[REDACTED]"
        elif isinstance(value, dict):
            event_dict[key] = _redact_dict(value)
    return event_dict


def _redact_dict(data: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for k, v in data.items():
        if str(k).lower() in REDACTED_KEYS:
            sanitized[k] = "[REDACTED]"
        elif isinstance(v, dict):
            sanitized[k] = _redact_dict(v)
        else:
            sanitized[k] = v
    return sanitized


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured logging for standard library and structlog."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        add_correlation_id,
        redact_sensitive_data,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=shared_processors + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processor=structlog.processors.JSONRenderer(),
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(level)

    # Silence overly verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str = "agentguard") -> structlog.stdlib.BoundLogger:
    """Return a configured structlog logger."""
    return structlog.get_logger(name)
