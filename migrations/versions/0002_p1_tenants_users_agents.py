"""P1 schema: users, memberships, agents, and agent credentials

Revision ID: 0002_p1_tenants_users_agents
Revises: 0001_initial
Create Date: 2026-11-22 09:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_p1_tenants_users_agents"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("external_subject", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("external_subject"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 2. tenant_memberships table
    op.create_table(
        "tenant_memberships",
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="operator"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "user_id"),
    )

    # 3. agents table
    op.create_table(
        "agents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("owner_user_id", sa.UUID(), nullable=True),
        sa.Column(
            "environment", sa.String(length=50), nullable=False, server_default="development"
        ),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column(
            "metadata_json",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "name", name="uq_agents_tenant_name"),
    )
    op.create_index("ix_agents_tenant_id", "agents", ["tenant_id"], unique=False)
    op.create_index("ix_agents_tenant_status", "agents", ["tenant_id", "status"], unique=False)

    # 4. agent_credentials table
    op.create_table(
        "agent_credentials",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("agent_id", sa.UUID(), nullable=False),
        sa.Column("credential_prefix", sa.String(length=16), nullable=False),
        sa.Column("credential_hash", sa.String(length=128), nullable=False),
        sa.Column(
            "scopes",
            sa.JSON().with_variant(postgresql.JSONB, "postgresql"),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("credential_hash", name="uq_agent_credentials_hash"),
    )
    op.create_index(
        "ix_agent_credentials_tenant_id", "agent_credentials", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_agent_credentials_agent_id", "agent_credentials", ["agent_id"], unique=False
    )
    op.create_index(
        "ix_agent_credentials_prefix", "agent_credentials", ["credential_prefix"], unique=False
    )


def downgrade() -> None:
    op.drop_table("agent_credentials")
    op.drop_table("agents")
    op.drop_table("tenant_memberships")
    op.drop_table("users")
