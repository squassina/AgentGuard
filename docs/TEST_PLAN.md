# AgentGuard — Test and Release Plan

**Version:** 0.1

## 1. Test pyramid

### Unit tests
- Policy matching and precedence.
- Canonical JSON argument hashing.
- Credential validation.
- Tenant context propagation.
- Approval state transitions.
- Secret redaction.
- URL/IP validation.
- MCP request validation.

### Integration tests
- PostgreSQL migrations and RLS.
- Agent credential lifecycle.
- Upstream MCP connection.
- Policy evaluation with real persistence.
- Approval persistence and atomic redemption.
- Audit event insertion and hash chain.
- Secrets manager adapter.
- Redis optionality.

### Protocol tests
- Initialize/initialized.
- Ping.
- Tools list.
- Tools call.
- Streamable HTTP framing and headers.
- Protocol version negotiation.
- Error responses.
- Notifications and cancellation behavior as supported by pinned revision.
- Interoperability with two independent MCP clients.

### End-to-end tests
- Agent connects through AgentGuard.
- Allowed tool executes exactly once.
- Denied tool does not execute.
- Approval-required tool waits for explicit decision.
- Approval causes one execution.
- Audit view shows full decision chain.

### Security tests
- Cross-tenant IDOR.
- Wrong-audience token.
- Expired/revoked token.
- Token passthrough check.
- SSRF and DNS rebinding.
- Approval replay and race.
- Policy service/database failure.
- Oversized request and response.
- Tool metadata XSS/injection.
- Header smuggling and hop-by-hop header handling.
- Rate limiting and concurrency abuse.
- Secret leakage in logs/traces/errors.

## 2. Critical test cases

| ID | Scenario | Expected |
|---|---|---|
| SEC-001 | No matching policy | Deny |
| SEC-002 | Explicit deny + allow both match | Deny |
| SEC-003 | Policy evaluator unavailable | Deny |
| SEC-004 | DB unavailable before decision audit | No upstream execution |
| SEC-005 | Wrong tenant agent ID | Reject without data disclosure |
| SEC-006 | Wrong token audience | 401 |
| SEC-007 | Inbound token supplied | Never forwarded upstream |
| SEC-008 | Private IP upstream target | Reject |
| SEC-009 | DNS rebinding to metadata IP | Reject |
| SEC-010 | Approval arguments changed | Reject |
| SEC-011 | Approval replay | At most one execution |
| SEC-012 | Approval expired | Reject |
| SEC-013 | Concurrent approval redemption | At most one execution |
| SEC-014 | Upstream timeout after request sent | Mark uncertain; no blind retry |
| SEC-015 | Oversized tool result | Truncate/reject per documented limit; audit |
| SEC-016 | Tool description contains HTML/script | Safely render; no authorization impact |
| SEC-017 | Agent revoked during operation | New requests rejected |
| SEC-018 | Tenant A queries Tenant B audit ID | Non-disclosing 404/403 policy |

## 3. Reliability and performance

- Unit test policy engine with boundary and property-based cases.
- Load test 50 RPS per small-tenant test profile.
- Measure p50/p95/p99 gateway overhead excluding upstream latency.
- Test 100 concurrent approval requests.
- Simulate DB, Redis and upstream outages.
- Verify bounded memory under large result and slow upstream.
- Ensure no unbounded background task or queue.

## 4. CI gates

Required on every PR:
1. Formatting.
2. Ruff lint.
3. Type checking.
4. Unit tests.
5. Integration tests with PostgreSQL.
6. Security tests.
7. Dependency vulnerability scan.
8. Container build.
9. Migration validation.

No merge with failing lint/tests/security checks. Keep tests deterministic; avoid network-dependent tests in the standard CI path.

## 5. Release gates

MVP cannot be called production-ready until:
- All critical security tests pass.
- No known critical/high exploitable findings remain.
- Tenant isolation tests pass.
- Backups and restore have been exercised.
- Secrets rotation is tested.
- OAuth audience validation is tested.
- Two independent MCP clients interoperate.
- Runbook covers policy failure, DB outage, upstream outage and credential compromise.
