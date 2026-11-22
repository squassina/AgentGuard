"""Unit tests for structured logging and secret redaction."""

from app.common.logging import (
    add_correlation_id,
    correlation_id_ctx,
    redact_sensitive_data,
)


def test_correlation_id_injected() -> None:
    """Verify correlation ID is added when present in context."""
    token = correlation_id_ctx.set("req-12345")
    try:
        event = add_correlation_id(None, "info", {"message": "test"})
        assert event["request_id"] == "req-12345"
    finally:
        correlation_id_ctx.reset(token)


def test_redact_sensitive_keys() -> None:
    """Verify sensitive fields are redacted."""
    event = {
        "user": "alice",
        "authorization": "Bearer secret-token",
        "nested": {
            "password": "super-secret-password",
            "safe_field": 123,
            "api_key": "my-secret-key",
        },
    }
    redacted = redact_sensitive_data(None, "info", event)
    assert redacted["user"] == "alice"
    assert redacted["authorization"] == "[REDACTED]"
    assert redacted["nested"]["password"] == "[REDACTED]"
    assert redacted["nested"]["api_key"] == "[REDACTED]"
    assert redacted["nested"]["safe_field"] == 123
