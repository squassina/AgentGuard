# AgentGuard — Product & Engineering Specification

**Version:** 0.1  
**Date:** 2026-11-21  
**Status:** Baseline for MVP implementation  
**Product name:** AgentGuard (working name; trademark/domain clearance pending)

## Package contents

- `PRD.md` — product requirements, users, scope, stories and acceptance criteria.
- `ARCHITECTURE.md` — system architecture, components, flows and operational decisions.
- `THREAT_MODEL.md` — assets, trust boundaries, threats and mandatory mitigations.
- `API_AND_DATA_MODEL.md` — API contracts, policy schema and initial database model.
- `TEST_PLAN.md` — test strategy, security cases and release gates.
- `ROADMAP.md` — phased delivery and validation milestones.
- `ADR.md` — architecture decision records.
- `AGENT_INSTRUCTIONS.md` — instructions for AI coding agents implementing the repository.

## Product summary

AgentGuard is a cloud-hosted MCP security gateway and control plane. It intercepts MCP tool calls, identifies the calling agent, evaluates deterministic policies, optionally requests human approval, forwards authorized calls to an upstream MCP server, and records an auditable decision trail.

**MVP wedge:** protect MCP `tools/call` operations for one customer tenant, using Streamable HTTP, deterministic allow/deny/approval policies, and a secure upstream connection.

## Non-goals

AgentGuard is not an agent orchestrator, LLM provider, SIEM, EDR, SOAR, general-purpose compliance platform, or prompt-injection detector. LLM inference is not part of the authorization decision path.

## Source-of-truth rule

The current MCP protocol and security requirements must be checked against the official specification before implementation and before each protocol upgrade:

- https://modelcontextprotocol.io/specification/2026-07-28
- https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization
- https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices

Do not silently implement an older MCP revision. Pin the chosen SDK and protocol revision, document compatibility, and test interoperability with at least two independent MCP clients.

## Implementation order

1. Threat model and protocol spike.
2. Minimal gateway vertical slice.
3. Tenant/authentication and agent identity.
4. Deterministic policy enforcement.
5. Approval workflow.
6. Audit evidence.
7. Dashboard, billing and commercial hardening.

Do not build a broad dashboard before the gateway can reliably block a tool call.
