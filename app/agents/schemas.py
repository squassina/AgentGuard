"""Pydantic schemas for agent and credential operations."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AgentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    environment: str = Field(default="development", pattern="^(development|staging|production)$")
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    environment: str | None = Field(default=None, pattern="^(development|staging|production)$")
    status: str | None = Field(default=None, pattern="^(active|disabled)$")
    metadata: dict[str, Any] | None = None


class AgentResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    owner_user_id: uuid.UUID | None = None
    environment: str
    status: str
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias="metadata_json",
        serialization_alias="metadata",
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CredentialCreate(BaseModel):
    scopes: list[str] = Field(default_factory=list)
    expires_at: datetime | None = None


class CredentialIssuedResponse(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    tenant_id: uuid.UUID
    credential_prefix: str
    raw_token: str = Field(description="Only displayed once upon creation!")
    scopes: list[str]
    expires_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CredentialResponse(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    tenant_id: uuid.UUID
    credential_prefix: str
    scopes: list[str]
    expires_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime
    last_used_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
