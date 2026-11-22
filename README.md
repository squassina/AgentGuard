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
