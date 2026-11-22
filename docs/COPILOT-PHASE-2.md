# Copilot Prompt — Roadmap Phase 2: Approval and Security Hardening

Complete the security controls required for production MVP. Read all files in `docs/`, inspect current code and tests, and preserve unrelated user changes. Follow `GLOSSARY.md`, ADR-013 through ADR-016, and the threat model when older documents conflict.

## Scope

- Production OAuth 2.1/OIDC validation for agents, including issuer, signature, expiry, audience, scopes, tenant binding, and registered-agent binding.
- Workforce identity validation for Control Plane users and verified tenant memberships. Remove header-trusted identity and any fallback administrator identity.
- Immutable policy versions, explicit publish/disable, rollback, and recorded decision version.
- Dashboard approval lifecycle with explicit tenant-scoped approver authority, five-minute default expiry, required rejection reason, and one-time retry redemption.
- Bind approvals to tenant, agent, upstream configuration revision, exact tool schema, canonical argument digest, policy version, and expiry.
- Invalidate approvals after relevant policy, identity, role, schema, upstream, or suspension changes.
- Per-upstream managed secret references, rotation/revocation, and no inbound token passthrough.
- Tenant isolation/RLS, safe egress and SSRF controls, append-only attributed audit events, per-tenant hash chains, and signed retention checkpoints.

## Security tests

Cover wrong issuer/audience, expiry and revocation, cross-tenant access, approval replay/races, changed arguments or bindings, policy changes, approver revocation, upstream/schema changes, suspension, SSRF, secret leakage, and audit-chain pruning.

## Completion criteria

- No upstream call occurs without an explicit allow or one successfully redeemed approval.
- No production identity comes from local static agent tokens or caller-supplied identity headers.
- No inbound token reaches an upstream.
- Duplicate approval retries cause at most one upstream invocation.
- Security tests and required lint, type checks, full tests, and container build pass. Report exact results and any unresolved risk.
