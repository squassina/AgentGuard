# AgentGuard — Architecture Decision Records

## ADR-001 — Modular monolith
**Status:** Accepted  
Use one codebase with clear modules. Avoid microservices until scaling or team boundaries justify them.

## ADR-002 — MCP Streamable HTTP only
**Status:** Accepted  
MVP supports remote Streamable HTTP. STDIO is excluded because it is a local process transport and requires a different interception/deployment model.

## ADR-003 — Gateway is the enforcement point
**Status:** Accepted  
All protected tool calls must traverse AgentGuard. Tool discovery filtering alone is not authorization.

## ADR-004 — Deterministic authorization
**Status:** Accepted  
No LLM can grant permission. Policy evaluation must be deterministic, testable and fail-closed.

## ADR-005 — Separate inbound and upstream credentials
**Status:** Accepted  
Never forward inbound bearer tokens. Upstream connections use separately provisioned credentials, scoped to their resource.

## ADR-006 — OAuth 2.1 / OIDC production authorization
**Status:** Accepted  
Production MCP HTTP authorization must conform to the pinned MCP authorization specification. Development-only tokens must be explicitly gated and cannot masquerade as standards-compliant OAuth.

## ADR-007 — PostgreSQL source of truth
**Status:** Accepted  
Persist tenants, agents, policies, approvals and audit events in PostgreSQL. Redis is optional and non-authoritative.

## ADR-008 — No OPA dependency in first MVP
**Status:** Accepted, revisit after pilot  
Use a small versioned deterministic policy evaluator. Revisit OPA when policy complexity and customer demand justify it.

## ADR-009 — Fail closed
**Status:** Accepted  
Missing policy, invalid policy, policy store failure, approval timeout or unavailable authorization dependency must not authorize a protected operation.

## ADR-010 — No arbitrary upstream URL
**Status:** Accepted  
MCP request data cannot choose an upstream endpoint. Upstreams are administrator-configured and network-validated.

## ADR-011 — No raw tool arguments in audit by default
**Status:** Accepted  
Store canonical argument digest and metadata. Optional redacted snapshots require explicit tenant configuration.

## ADR-012 — Existing project reuse is conditional
**Status:** Accepted  
OpenShield-luna and AMASDO are potential sources of patterns/components, not runtime dependencies. Reuse requires code review, license review, security review and independent tests.

## ADR-013 — Customer-controlled production identities
**Status:** Accepted
Production agent authentication uses customer OAuth/OIDC claims bound to tenant-scoped Agent registrations, and human control-plane access uses workforce identity with tenant memberships. AgentGuard-issued production tokens and caller-supplied identity headers are not authoritative; isolated development/test credentials may remain.

## ADR-014 — Shared tenant boundary
**Status:** Accepted
MVP uses shared cloud services with Tenant as the root ownership and isolation boundary. Dedicated customer deployments are out of MVP.

## ADR-015 — Exact one-time approvals
**Status:** Accepted
An approval authorizes one exact tool call and binds to its tenant, agent, upstream configuration, tool schema, arguments, and policy version. It expires, can be redeemed once, and is invalidated by relevant identity or configuration changes; callers retry after dashboard review instead of the gateway invoking asynchronously.

## ADR-016 — Tamper-evident audit chain
**Status:** Accepted
Application audit events are append-only and hash-chained per tenant; retention pruning uses signed checkpoints. This provides tamper evidence, not protection from privileged database operators.
