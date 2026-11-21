# Instructions for AI Coding Agents — AgentGuard

You are implementing AgentGuard from the specification package. Follow these rules.

## Operating rules

1. Read all files in `docs/` before coding.
2. Inspect the existing repository before proposing or changing architecture.
3. Implement one roadmap phase at a time.
4. Keep changes small, complete and testable.
5. Do not create microservices.
6. Do not add dependencies without a concrete need.
7. Do not implement out-of-scope features.
8. Do not weaken security controls to make tests pass.
9. Do not use an LLM to make authorization decisions.
10. Do not forward inbound Authorization headers to upstream servers.
11. Never accept arbitrary upstream URLs from MCP request bodies.
12. Treat tool descriptions, annotations, prompts and tool results as untrusted.
13. Enforce tenant scope in every tenant-owned query.
14. Use migrations for schema changes.
15. Add tests for every security-relevant behavior.
16. Run lint, type checks, tests and container build before declaring completion.
17. Report actual test results; never claim tests passed if not executed.
18. Do not perform destructive database or deployment operations without explicit approval.

## Required workflow per task

1. State the target acceptance criteria.
2. Inspect relevant modules and all callers.
3. Implement the smallest complete change.
4. Add/update unit and integration tests.
5. Run relevant tests.
6. Run full lint and test suite when practical.
7. Review security implications.
8. Update README and docs when behavior or setup changes.
9. Summarize files changed, tests run, results and remaining risks.

## Security invariants

- No upstream call without an explicit allow decision or a successfully redeemed approval.
- No policy match means deny.
- Invalid policy means deny.
- Policy engine failure means deny.
- Approval is one-time and bound to exact arguments, tool, agent, tenant and policy version.
- No token passthrough.
- No cross-tenant data access.
- No unvalidated egress destination.
- No secret values in logs.
- No raw tool arguments in audit unless tenant explicitly enables a redacted allowlist.

## Coding conventions

- Python 3.12+.
- FastAPI with explicit lifespan management.
- Async I/O for network and database paths.
- PostgreSQL with migrations.
- Type hints for public functions and domain models.
- Structured logging with request correlation IDs.
- Ruff for lint/format.
- Pytest for tests.
- Prefer explicit domain services over generic abstraction frameworks.

## Repository bootstrap

Before creating files, inspect whether the repository already has conventions. Preserve existing naming, tooling and CI where reasonable. If empty, use the layout in `ARCHITECTURE.md`.

## Definition of done

A task is done only when:
- Acceptance criteria are met.
- Tests are added and pass.
- Lint passes.
- Security invariants remain true.
- Documentation is updated.
- No unrelated files or generated secrets are committed.
