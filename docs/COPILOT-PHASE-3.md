# Copilot Prompt — Roadmap Phase 3: Pilot Readiness

Prepare AgentGuard for a controlled customer pilot. Read all files in `docs/`, inspect existing code and the current worktree, and preserve unrelated changes. Verify that Phase 1 and Phase 2 acceptance criteria are met before expanding scope.

## Scope

- Basic tenant administration and onboarding.
- Agent, upstream, policy, membership, and approver management.
- Dashboard approval review with redacted request context.
- Searchable tenant-scoped audit history with integrity verification.
- Basic usage counters, health/readiness behavior, operator documentation, and support runbook.
- Pilot setup and teardown instructions that require explicit user approval for external or destructive actions.

Billing, customer notifications, and exportable audit reports remain P1 unless the user approves an evidence-based exception.

## Execution rules

- Never claim that pilots, paid conversions, customer acceptance, or measured commercial outcomes occurred unless the user provides evidence.
- Do not contact customers, create accounts in external services, deploy production infrastructure, or incur charges without explicit approval.
- Keep all admin actions tenant-scoped and auditable.
- Use redacted approval context and digest-only audit arguments by default.
- Add integration and usability tests for onboarding, approval review, audit search, and tenant boundaries.

## Completion criteria

- A technical user can follow the documented path to a protected tool call in a test environment.
- An authorized approver can review and decide a request; the agent must retry to execute it.
- A tenant auditor can find attributed decision and execution events without accessing another tenant's data.
- Readiness gaps and unverified commercial exit criteria are reported separately from implemented features.
