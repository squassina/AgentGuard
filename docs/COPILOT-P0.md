# Copilot Prompt — P0 Required MVP

Implement AgentGuard's required MVP scope. Treat this as the P0 acceptance contract, not permission to skip repository investigation.

## Before changing code

1. Read all files in `docs/`, including `AGENT_INSTRUCTIONS.md`, `PRD.md`, `ROADMAP.md`, `ARCHITECTURE.md`, `API_AND_DATA_MODEL.md`, `THREAT_MODEL.md`, `TEST_PLAN.md`, `ADR.md`, and `GLOSSARY.md`.
2. Inspect the current worktree and relevant callers. Preserve unrelated user changes.
3. Use `GLOSSARY.md` and ADR-013 through ADR-016 as confirmed domain decisions. They supersede older PRD or roadmap statements that conflict with them.
4. Update stale scope statements in the PRD and roadmap as needed. Do not silently restore moved features to P1 or Phase 4.
5. Implement in small, complete vertical slices. Report blockers that require customer credentials, external research, or user decisions; never invent their results.

## Required domain and security behavior

- Treat `Tenant` as the shared-cloud ownership and isolation boundary.
- Authenticate human identities through customer workforce identity. Key each identity by verified issuer and subject; grant roles through tenant memberships.
- Authenticate agents through customer OAuth/OIDC claims bound to tenant-scoped Agent registrations. Authenticate every HTTP request. Keep local credentials development-only.
- Support remote MCP Streamable HTTP. Do not add STDIO or arbitrary TCP proxying.
- Support multiple administrator-configured upstreams per tenant. Use a separate managed credential for each upstream; never forward inbound credentials or accept a caller-supplied upstream URL.
- Discover tools from upstreams and treat descriptions, schemas, results, and other metadata as untrusted. Identify each tool by `(upstream_id, tool_name)`.
- Filter `tools/list` to tools with an allow or approval path. Independently authorize every `tools/call`.
- Evaluate deterministic, tenant-owned policies. Published versions are immutable; edits require explicit publish, and prior versions can be reactivated. Match exact tool identities only. Resolve conflicts as `deny`, then `require_approval`, then `allow`. No match, invalid policy, or evaluator failure denies.
- Separate each authorization decision from its upstream execution outcome.
- Use a Control Plane approval workflow with explicit tenant-scoped approver permission. An approval authorizes one exact call, expires after five minutes by default, and can be redeemed once. Bind it to tenant, agent, upstream configuration, tool schema, canonical argument digest, policy version, and expiry. Require the caller to retry with a one-time reference after approval.
- Invalidate pending or approved-but-unexecuted requests after relevant policy, identity, approver-role, tool-schema, upstream-configuration, or suspension changes. Rejection, expiry, and cancellation are terminal. Require a rejection reason.
- Record every tool-call attempt and security-relevant control-plane change as attributable append-only audit events. Hash-chain events per tenant and preserve verification with signed checkpoints when retention prunes data. Store argument digests by default; expose only redacted approval context.
- Enforce tenant-scoped queries, safe egress/SSRF controls, secret redaction, fail-closed behavior, and no duplicate upstream execution.

## Acceptance criteria

1. A verified external agent maps to exactly one tenant-scoped registration for that tenant; a human has only the roles granted by verified tenant membership.
2. Tenant A cannot read or change Tenant B's records.
3. Allowed calls reach the configured upstream once. Denied calls never reach it.
4. `tools/list` filtering never replaces call-time authorization.
5. A missing, invalid, or unavailable policy denies the protected call.
6. Approval cannot execute before approval, after expiry or revocation, with changed arguments or bindings, or more than once.
7. An ambiguous upstream result is recorded as uncertain; non-idempotent operations are not retried automatically.
8. Inbound credentials, secrets, and raw arguments do not appear in logs or default audit payloads.
9. Audit evidence covers allow, deny, approval, execution failure, and security-relevant configuration changes.
10. Tests cover tenant isolation, OAuth/OIDC claim validation, policy precedence, approval races/replay, schema and configuration changes, SSRF, and audit-chain pruning.
11. Run the relevant tests, lint, type checks, and container build required by `AGENT_INSTRUCTIONS.md`. Report exact results and remaining blockers.

Do not declare P0 complete while any acceptance criterion or external prerequisite remains unverified.
