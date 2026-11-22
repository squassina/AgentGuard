"""Unit tests for agent credential cryptography."""

from app.auth.security import generate_agent_token, hash_credential, verify_credential


def test_generate_agent_token_development() -> None:
    raw_token, prefix, token_hash = generate_agent_token("development")
    assert raw_token.startswith("ag_dev_")
    assert prefix == raw_token[:12]
    assert len(token_hash) == 64
    assert hash_credential(raw_token) == token_hash
    assert verify_credential(raw_token, token_hash) is True


def test_generate_agent_token_production() -> None:
    raw_token, prefix, token_hash = generate_agent_token("production")
    assert raw_token.startswith("ag_live_")
    assert prefix == raw_token[:12]
    assert verify_credential(raw_token, token_hash) is True


def test_verify_credential_negative() -> None:
    raw_token, _, token_hash = generate_agent_token("development")
    assert verify_credential("wrong_token", token_hash) is False
    assert verify_credential(raw_token + "extra", token_hash) is False
