# AgentGuard — Roadmap and Validation Plan

**Version:** 0.1 | **Planning horizon:** 90 days to paid pilot; 6 months to expansion

## Phase 0 — Discovery and protocol spike (Weeks 1–2)

Deliverables:
- 15–20 buyer interviews.
- 3 candidate design partners.
- Confirm cloud gateway acceptability.
- Confirm MCP clients and protocol revisions in use.
- Minimal protocol proxy spike.
- Demonstration of allow/deny.

Exit criteria:
- At least 10 interviewees confirm meaningful control gap.
- At least 3 agree to pilot discussions.
- At least 1 customer accepts gateway in traffic path.
- Technical spike can proxy a tool call and block it before upstream execution.

Stop/rethink if customers will not route traffic through a third-party cloud gateway.

## Phase 1 — Core gateway (Weeks 3–6)

Deliverables:
- Repository and CI.
- FastAPI application.
- MCP Streamable HTTP endpoint.
- One upstream MCP server.
- Agent identity.
- Tool discovery.
- Deterministic policy engine.
- Allow/deny enforcement.
- Initial audit records.
- PostgreSQL migrations.

Exit criteria:
- Allow executes exactly once.
- Deny never reaches upstream.
- Missing/invalid policy denies.
- Protocol tests pass.

## Phase 2 — Approval and security hardening (Weeks 7–9)

Deliverables:
- Approval workflow.
- One-time approval redemption.
- Argument digest binding.
- Credential rotation/revocation.
- SSRF protection.
- Tenant isolation/RLS.
- Secret manager integration.
- OAuth/OIDC production profile.
- Security test suite.

Exit criteria:
- Replay/race tests pass.
- No inbound token passthrough.
- Wrong audience rejected.
- Critical security tests pass.

## Phase 3 — Pilot and commercial launch (Weeks 10–13)

Deliverables:
- Basic admin UI.
- Customer onboarding.
- Audit search.
- Usage counters.
- Billing integration only if required by first paid pilots.
- Docs and support runbook.
- 2 active pilots.
- 2 paid conversions or signed paid-pilot commitments.

Exit criteria:
- Customers deploy a real agent.
- At least one protected write operation uses approval.
- Measured latency and reliability are acceptable.
- Customer confirms willingness to continue paying.

## Phase 4 — Expansion (Months 4–6)

Only after product-market evidence:
- Multiple upstream MCP servers.
- Policy templates.
- Policy version rollback.
- SSO/SCIM.
- Notifications.
- More MCP clients and SDK examples.
- Audit export.
- Usage-based pricing.
- MSP/consultancy partner discovery.

## Commercial validation cadence

Weekly:
- 10 qualified outbound contacts.
- 3–5 discovery conversations.
- 1 product demo.
- Review objections and lost deals.
- Update ICP and pricing hypotheses.

Monthly:
- Pilot-to-paid conversion.
- Active agents per tenant.
- Protected tool calls.
- Deny/approval rates.
- Gateway p95 latency.
- Gross margin per tenant.
- Support hours per customer.

## Kill / pivot criteria

Reassess product direction if:
- Fewer than 3 prospects agree to pilot after 20 qualified interviews.
- No prospect accepts cloud gateway placement.
- Customers consistently consider existing platform controls sufficient.
- Integration effort exceeds the value delivered.
- No paid pilot after 3 technically successful pilots.
