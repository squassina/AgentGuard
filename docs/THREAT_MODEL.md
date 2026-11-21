# AgentGuard — Threat Model

**Version:** 0.1 | **Method:** STRIDE + abuse cases

## 1. Security objectives

- Only authenticated, authorized agents can invoke configured tools.
- A tool call cannot bypass policy enforcement.
- A caller cannot choose another tenant or upstream by modifying request data.
- Approval applies to exactly one operation and cannot be replayed.
- Credentials are never leaked through logs, errors or token passthrough.
- Gateway failure cannot silently authorize protected operations.
- Audit evidence is complete enough to reconstruct decisions.

## 2. Assets

1. Inbound agent credentials.
2. Upstream MCP credentials and OAuth refresh tokens.
3. Tenant data and policy definitions.
4. Tool arguments and results.
5. Approval decisions and nonces.
6. Audit events.
7. Upstream endpoint configuration.
8. Signing keys, encryption keys and database credentials.
9. Control plane administrator sessions.

## 3. Trust boundaries

- Internet/client to AgentGuard ingress.
- Tenant A to tenant B.
- Control plane to data plane.
- AgentGuard to upstream MCP server.
- Application to database/cache.
- Application to secrets manager.
- Human approver to approval API.
- Build pipeline to production deployment.

## 4. Threats and mitigations

### T1 — Cross-tenant data access
Threat: caller changes tenant/agent IDs or exploits missing tenant filter.
Mitigations:
- derive tenant from verified identity;
- enforce tenant-scoped repository methods;
- PostgreSQL RLS as defense in depth;
- no tenant ID accepted as an authorization source from request body;
- negative tests across every tenant-owned endpoint.

### T2 — Credential theft
Threat: inbound or upstream token exposed in logs, traces, DB or error messages.
Mitigations:
- TLS;
- secret manager/KMS;
- hash inbound opaque credentials;
- never log Authorization/Cookie headers;
- redact known secret fields;
- short-lived tokens and rotation;
- separate inbound and upstream credentials.

### T3 — Token passthrough / confused deputy
Threat: gateway forwards an inbound token to a different upstream resource.
Mitigations:
- never forward inbound bearer token;
- separate upstream OAuth client/credential;
- validate issuer and audience;
- bind tokens to intended resource;
- use explicit per-upstream credential references.

### T4 — SSRF through upstream URL
Threat: malicious admin input or compromised tenant targets cloud metadata, localhost, private ranges or internal control services.
Mitigations:
- strict URL parser;
- HTTPS required in production;
- DNS resolution and IP validation;
- block loopback, link-local, multicast, unspecified and cloud metadata ranges;
- revalidate resolved IP at connection time;
- defend against DNS rebinding;
- allowlist destinations;
- no redirects by default; if enabled, revalidate every hop;
- outbound network policy.

### T5 — Tool poisoning / malicious metadata
Threat: upstream tool description or annotations manipulate agent or gateway behavior.
Mitigations:
- treat names/descriptions/annotations as untrusted display data;
- never derive authorization from tool descriptions;
- policy matches stable tool identifier and admin-authored constraints;
- sanitize UI rendering;
- enforce response size limits.

### T6 — Argument manipulation / schema confusion
Threat: attacker changes arguments after approval or exploits ambiguous JSON.
Mitigations:
- canonical JSON serialization;
- reject duplicate keys and invalid types;
- bind approval to SHA-256 of canonical arguments;
- revalidate schema immediately before execution;
- reject changed arguments;
- include tool/upstream/policy version in approval binding.

### T7 — Approval replay/race
Threat: same approval executes multiple times or across agents/tenants.
Mitigations:
- cryptographically random one-time nonce;
- database conditional state transition;
- row lock/atomic compare-and-swap;
- expiry;
- bind to exact tenant/agent/tool/arguments/policy version;
- concurrency tests.

### T8 — Fail-open on dependency failure
Threat: policy engine, DB, identity provider or approval service unavailable.
Mitigations:
- fail closed for protected operations;
- no cached allow beyond explicit short-lived policy cache rules;
- policy version and cache invalidation;
- fail-closed integration tests;
- safe 503/authorization errors.

### T9 — Replay of MCP requests
Threat: duplicated client request executes non-idempotent operation twice.
Mitigations:
- request correlation IDs;
- idempotency handling where protocol and upstream permit;
- do not blindly retry non-idempotent tool calls;
- uncertain execution state after network interruption;
- explicit upstream timeout semantics.

### T10 — Resource exhaustion
Threat: oversized bodies, tool results, long-running calls or request floods.
Mitigations:
- body/result size caps;
- per-tenant rate limits and concurrency limits;
- connection/read/write timeouts;
- bounded queues;
- quotas;
- cancellation propagation where supported.

### T11 — Audit tampering or omission
Threat: operator modifies/deletes records or an execution path fails to log.
Mitigations:
- append-only application DB role;
- transactionally record decision before forwarding;
- record final outcome separately;
- hash chaining or signed batches;
- export to customer-controlled storage later;
- alert on audit writer failure; do not execute if required decision audit cannot be persisted.

### T12 — Malicious tool result
Threat: upstream returns prompt injection or malicious content that influences the agent.
Mitigations:
- return data without treating it as instructions;
- do not claim the gateway neutralizes prompt injection;
- optional output scanning is out of MVP;
- document that downstream agent remains responsible for safe interpretation.

### T13 — Admin account compromise
Threat: attacker changes policies or upstream credentials.
Mitigations:
- MFA/SSO for production admin accounts;
- RBAC;
- re-authentication for credential/policy changes;
- audit every admin mutation;
- secret rotation;
- least privilege.

### T14 — Supply chain compromise
Threat: compromised dependency, container or CI workflow.
Mitigations:
- pinned dependencies;
- lockfile;
- dependency scanning;
- SBOM;
- image scanning;
- signed release artifacts when feasible;
- protected main branch and CI gates.

## 5. Security invariants

1. No upstream call before a positive authorization decision.
2. No upstream call after deny, expiry, rejection or policy error.
3. No authorization from unverified tenant/agent identifiers.
4. No inbound credential forwarded upstream.
5. No approval reused.
6. No arbitrary upstream URL from MCP request.
7. No LLM-generated allow decision.
8. No raw secrets in logs.
9. No cross-tenant query without tenant scope.
10. No silent fail-open.

## 6. Abuse cases for security tests

- Agent A calls tool registered only for Agent B.
- Tenant A uses Tenant B's agent ID.
- Caller changes arguments after approval.
- Two concurrent requests redeem one approval.
- Upstream URL resolves to 169.254.169.254.
- DNS answer changes from public to private IP.
- Upstream returns huge result.
- Policy store unavailable during a write operation.
- Token has wrong audience.
- Token is expired or revoked.
- Upstream redirects to a private IP.
- Tool description contains malicious HTML or instructions.
- Client sends Authorization token for upstream API; verify it is not forwarded.
- Gateway restarts between approval and execution.
