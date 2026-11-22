# AgentGuard

AgentGuard is a cloud-hosted MCP Security Gateway and Control Plane. It intercepts Model Context Protocol (MCP) tool calls, authenticates the calling agent, evaluates deterministic security policies, enforces authorization, coordinates human approvals, and generates auditable security events.

## Prerequisites

- Python 3.12+ (or [uv](https://github.com/astral-sh/uv))
- Docker & Docker Compose
- PostgreSQL 16+ (for local bare-metal run)

## Quickstart with Docker Compose

1. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```
2. Start the services (PostgreSQL + AgentGuard application):
   ```bash
   docker compose up --build
   ```
3. Verify health checks:
   ```bash
   curl http://localhost:8000/health/live
   curl http://localhost:8000/health/ready
   ```

## Local Development Setup

1. Install dependencies using `uv`:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

2. Start PostgreSQL:
   ```bash
   docker compose up -d postgres
   ```

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

4. Start the application:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Overview

- **Health:**
  - `GET /health/live`: Liveness probe.
  - `GET /health/ready`: Readiness probe verifying PostgreSQL connection.
  - `GET /metrics`: Service metrics probe.
- **Tenants:**
  - `POST /api/v1/tenants`: Create a tenant.
  - `GET /api/v1/tenants/{tenant_id}`: Retrieve tenant details.
- **Agents:**
  - `POST /api/v1/agents`: Register an agent (scoped to `X-Tenant-ID`).
  - `GET /api/v1/agents`: List tenant agents (supports `environment` and `status` filters).
  - `GET /api/v1/agents/{agent_id}`: Retrieve agent details.
  - `PATCH /api/v1/agents/{agent_id}`: Update agent metadata, environment, or status.
  - `POST /api/v1/agents/{agent_id}/credentials`: Issue a new credential (raw token displayed only once).
  - `GET /api/v1/agents/{agent_id}/credentials`: List agent credential metadata.
  - `POST /api/v1/agents/{agent_id}/credentials/{credential_id}/rotate`: Atomically rotate credential.
  - `DELETE /api/v1/agents/{agent_id}/credentials/{credential_id}`: Revoke credential.
  - `POST /api/v1/agents/{agent_id}/revoke`: Revoke agent and all associated active credentials.

## Quality and Testing

- **Lint and format checks:**
  ```bash
  ruff check .
  ruff format --check .
  ```
- **Run tests:**
  ```bash
  pytest
  ```

## Project Structure

```text
agentguard/
  app/
    api/            # API routers and endpoints
    gateway/        # MCP proxy, protocol handler, upstream connections
    auth/           # Authentication and machine credentials
    agents/         # Agent registry and lifecycle
    policies/       # Deterministic policy engine
    approvals/      # Human approval queue and validation
    audit/          # Tamper-evident audit trail
    tenants/        # Multi-tenant scoping and RLS
    secrets/        # Secrets management adapters
    common/         # Shared utilities (config, logging, db)
  migrations/       # Alembic migrations
  tests/            # Unit, integration, security and protocol tests
  docs/             # Specifications and architecture baseline
```
