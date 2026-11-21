# Product Requirements Document — AgentGuard

**Version:** 0.1 | **Date:** 2026-11-21 | **Status:** Approved baseline for MVP planning

## 1. Vision

Provide a cloud security control plane that intercepts MCP tool calls and enforces deterministic authorization before an AI agent can execute an operation.

**Promise:** Every protected agent action is identified, evaluated, authorized and auditable.

## 2. Problem

Organizations connect AI agents to business systems through tools and MCP servers. Existing controls often focus on model safety, identity, discovery, or monitoring. Customers need an operational control point that can make a deterministic decision before a tool operation executes.

The MVP addresses:
- Unknown or over-privileged agents.
- Unrestricted access to sensitive tools.
- Lack of approval for destructive or high-impact operations.
- Insufficient evidence of who requested an action and which policy authorized or denied it.

## 3. Target customer and buyer

### Initial ICP
- B2B SaaS and AI-native companies.
- 20–200 employees; 10–100 engineers.
- At least one MCP-enabled agent in production or advanced pilot.
- Agents access business data or perform write operations.
- Cloud-first infrastructure.

### Buying roles
- Economic buyer: CTO, CISO, founder.
- Champion: AI Engineering Lead, Platform Engineer, Security Engineer.
- Operator: developer or security administrator.

## 4. Product boundary

AgentGuard is:
- An MCP Streamable HTTP gateway/proxy.
- An agent registry with machine identity.
- A deterministic policy enforcement point.
- A human approval workflow for selected actions.
- An audit event service.

AgentGuard is not:
- An LLM runtime or agent orchestrator.
- A prompt injection detection product.
- A SIEM/EDR/SOAR.
- A generic compliance platform.
- A universal proxy for arbitrary network protocols.

## 5. MVP scope

### P0 — Required
1. Tenant and user identity.
2. Agent registry and credential lifecycle.
3. Register one upstream MCP server per gateway route.
4. MCP Streamable HTTP ingress.
5. Support required protocol initialization and tool discovery/call methods for the pinned MCP revision.
6. Intercept `tools/call`.
7. Deterministic policy evaluation: `allow`, `deny`, `require_approval`.
8. Default deny when no applicable policy exists.
9. Human approval with expiry and one-time execution semantics.
10. Upstream call using a separately configured upstream credential.
11. Audit decision and execution outcome.
12. Tenant isolation.
13. Basic admin UI for agents, upstreams, policies, approvals and audit events.
14. Health/readiness endpoints and structured logs.

### P1 — After pilot validation
- Multiple upstream servers per tenant.
- Policy versioning and rollback.
- OIDC/SSO for human administrators.
- OAuth authorization server integration for MCP clients, including protected resource metadata and audience-bound tokens.
- Usage metering and billing.
- Notifications for approval requests.
- Exportable audit reports.

### Explicitly excluded from MVP
- STDIO proxying.
- Arbitrary TCP proxy.
- LLM-based policy decisions.
- Automatic prompt injection detection.
- SIEM/SOAR integrations.
- Agent discovery across the whole enterprise network.
- Self-hosted/on-prem deployment.
- Full OAuth federation for every upstream provider.
- General-purpose workflow builder.
- Multiple policy languages.

## 6. Protocol and authorization constraint

The product targets the official MCP revision `2026-07-28` and Streamable HTTP. Pin the exact Python SDK version and protocol behavior in the repository.

The MCP HTTP authorization specification uses OAuth 2.1 security practices, protected resource metadata, authorization server discovery and resource/audience binding. Never forward an inbound bearer token to an upstream MCP server. Upstream credentials must be independent and scoped to the upstream resource.

For local development, test credentials may be used behind a development-only configuration. Production must not silently substitute static API keys for an OAuth flow while claiming MCP authorization conformance. If the first pilot uses an explicitly documented non-conformant service-token profile, label it as such and gate it behind a feature flag; do not expose it as standards-compliant OAuth.

## 7. Core user stories

- As an admin, I can register an agent and issue/revoke its credential.
- As an admin, I can register an upstream MCP server and configure its independent credentials.
- As an admin, I can define allowed tools and action-specific policies.
- As a security operator, I can require human approval for sensitive tool calls.
- As a developer, I can configure an MCP client to use the AgentGuard endpoint.
- As an auditor, I can inspect the identity, tool, policy version, decision and execution result for each call.
- As a tenant admin, I cannot access another tenant's agents, policies, approvals or audit records.

## 8. Functional requirements

### FR-01 Agent identity
Each agent has immutable ID, tenant ID, display name, status, owner, environment and credential metadata. Credentials are displayed only once, stored hashed where possible, scoped to a tenant and agent, revocable, and rotated without downtime.

### FR-02 Upstream registration
Each upstream record contains tenant ID, endpoint, transport type, connection status, credential reference, timeout and allowed network destinations. Secret values are stored in a secrets manager or envelope-encrypted; never plaintext in the database.

### FR-03 Tool discovery
Gateway obtains upstream tool definitions and exposes a filtered list. Tool names and descriptions are untrusted input. They must not influence authorization except as identifiers matched against administrator-authored policy.

### FR-04 Tool call enforcement
Every `tools/call` must:
1. Authenticate the client.
2. Resolve tenant and agent from verified identity, never from caller-supplied JSON.
3. Resolve upstream and tool.
4. Validate request size/schema.
5. Evaluate a deterministic policy.
6. Deny, await approval, or execute.
7. Record decision and outcome.

### FR-05 Policy behavior
- Explicit deny overrides allow.
- No matching policy means deny.
- Invalid policy means deny and alert.
- Policy engine timeout/error means deny for protected operations.
- Approval is required only when an explicit policy says so.
- An approval is bound to one tenant, agent, tool, canonical argument digest, policy version and expiry.
- Any argument change invalidates approval.
- Approval cannot be replayed.

### FR-06 Approval
Approvals have `pending`, `approved`, `rejected`, `expired`, `executed`, `execution_failed`, `cancelled` states. A decision is immutable. Approval expiry defaults to 5 minutes and is configurable within safe bounds. The gateway must not hold an unbounded HTTP request open; use an explicit pending response/task mechanism compatible with the pinned MCP revision, or return a structured retryable response and require a fresh call after approval. Do not execute the original call asynchronously without a well-defined client-visible result.

### FR-07 Audit
Record request ID, tenant, agent, upstream, tool, argument digest, policy ID/version, decision, reason code, approval reference, timestamps, latency, upstream status and outcome. Do not log raw arguments or secrets by default. Audit records must be append-only at the application layer and tamper-evident.

### FR-08 Administration
Admin UI supports CRUD for agents, upstreams and policies; approval review; searchable audit events; credential rotation/revocation.

## 9. Non-functional requirements

- Security: tenant isolation, least privilege, secure secrets, fail-closed enforcement.
- Availability: target 99.5% monthly MVP service availability, excluding planned maintenance.
- Latency: gateway overhead p95 under 100 ms for local policy evaluation, excluding upstream latency, under pilot load.
- Throughput: establish baseline at 50 requests/sec per small tenant in load tests; do not market this as a limit until measured.
- Reliability: no duplicate execution caused by approval retries or gateway retries.
- Observability: traces, metrics and structured logs with correlation IDs.
- Privacy: configurable retention; redact sensitive arguments; do not use customer payloads for model training.
- Portability: containerized deployment, managed PostgreSQL, optional Redis.

## 10. Acceptance criteria

MVP is accepted only when:
1. A valid registered agent can initialize and list permitted tools.
2. An allowed tool call reaches the configured upstream exactly once.
3. A denied tool call never reaches upstream.
4. A tool call requiring approval is not executed before approval.
5. Rejected, expired, replayed or argument-modified approvals never execute.
6. Missing policy, invalid policy and policy engine failure deny protected calls.
7. Inbound credentials are never forwarded to upstream.
8. Cross-tenant access attempts return a non-disclosing authorization failure.
9. Audit evidence exists for allow, deny, approval and upstream failure outcomes.
10. Secrets and raw sensitive arguments do not appear in logs.
11. Gateway rejects SSRF attempts, private/link-local/metadata destinations unless explicitly allowed by an administrator under a safe network policy.
12. Integration tests pass against at least two independent MCP clients and one test upstream server.

## 11. Success metrics

### Product
- Time to first protected MCP tool call: under 30 minutes for a technical user.
- Percentage of protected calls with complete decision evidence: 100%.
- False allow rate in security test suite: 0.
- Approval replay success: 0.
- Gateway overhead p95: under 100 ms in agreed test environment.

### Commercial validation
- 15–20 buyer interviews.
- 3 design partners.
- At least 2 active pilots.
- At least 2 paid conversions or signed paid-pilot commitments before expanding scope.
- Evidence that customers accept the cloud gateway in the execution path.

## 12. Open questions to resolve during discovery

- Will customers route production MCP traffic through a third-party cloud gateway?
- Which MCP clients and SDK versions are present in target accounts?
- Do buyers require customer-managed OAuth authorization servers at launch?
- What data may be retained in audit events?
- Is approval UX required in the MCP client, web dashboard, or both?
- Which upstream credential patterns are common in the first ICP?
