# Copilot Prompt — Roadmap Phase 1: Core Gateway

Implement the core gateway vertical slice. Read all files in `docs/`, inspect the current worktree and relevant modules, and preserve unrelated user changes. Use the confirmed glossary and ADR-013 through ADR-016 over older conflicting scope statements.

## Scope

- FastAPI application and PostgreSQL migrations.
- Remote MCP Streamable HTTP ingress for the pinned protocol revision.
- Tenant-scoped agent and upstream records. Design for multiple upstreams per tenant, even when validating the first vertical slice with one.
- A development-only test identity path behind explicit configuration. Keep production ingress unavailable until Phase 2 completes standards-based OAuth/OIDC validation.
- `tools/list` discovery filtering and independent `tools/call` authorization.
- Deterministic policy evaluation with exact `(upstream_id, tool_name)` matching, explicit deny precedence, and default-deny behavior.
- Initial append-only decision and execution audit events.

## Invariants

- Derive tenant and agent identity from verified authentication context, never caller-supplied request data.
- Resolve upstreams only through administrator-configured tenant routes.
- Treat upstream tool metadata as untrusted.
- Never forward inbound credentials or call an arbitrary endpoint.
- An allow reaches the test upstream exactly once; a deny never reaches it.
- Policy absence, invalidity, or evaluator failure denies. `require_approval` never executes without a redeemed approval.

## Completion criteria

- Migrations and domain services support tenant isolation and the stated resource relationships.
- Protocol integration tests cover initialize, discovery, allowed calls, denied calls, and error handling.
- Unit tests cover exact tool matching, deterministic decisions, and default deny.
- Tests prove that listing a tool does not authorize its invocation.
- Run the repository-required checks and report exact results. Do not claim production readiness before Phase 2 security work.
