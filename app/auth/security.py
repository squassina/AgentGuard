"""Cryptographic utilities for agent credentials."""

import hashlib
import hmac
import secrets


def generate_agent_token(environment: str = "development") -> tuple[str, str, str]:
    """Generate an opaque high-entropy token, returning (raw_token, prefix, hash).

    Prefix distinguishes environment: 'ag_live_' or 'ag_dev_'.
    Returns:
        raw_token: displayed only once to caller
        prefix: short string for indexing and diagnostics
        hash: SHA-256 digest hex string stored in database
    """
    env_tag = "live" if environment == "production" else "dev"
    random_part = secrets.token_urlsafe(32)
    raw_token = f"ag_{env_tag}_{random_part}"
    prefix = raw_token[:12]
    token_hash = hash_credential(raw_token)
    return raw_token, prefix, token_hash


def hash_credential(raw_token: str) -> str:
    """Compute constant-length SHA-256 digest of credential."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def verify_credential(raw_token: str, stored_hash: str) -> bool:
    """Verify raw token against stored hash using constant-time comparison."""
    computed = hash_credential(raw_token)
    return hmac.compare_digest(computed, stored_hash)
