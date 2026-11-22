# Copilot Prompt — P1 Post-Pilot Features

Implement only the remaining P1 features after pilot validation and explicit user approval. First inspect the repository, current worktree, P0 acceptance status, and all files in `docs/`.

## Scope

P1 covers:

- Usage metering and billing.
- Approval request notifications.
- Exportable audit reports.

The following features were promoted into MVP by the confirmed domain model. Do not defer or rebuild them as P1 work: multiple upstreams per tenant, immutable policy versions and rollback, customer OAuth/OIDC for agents, and workforce identity for human administrators.

## Execution rules

1. Confirm with the user that pilot validation supports starting P1. If evidence is absent, prepare a readiness report and stop before implementing product features.
2. Define measurable acceptance criteria for each selected P1 feature before coding.
3. Keep billing behind an explicit provider/configuration boundary. Do not create real charges or contact customers without direct approval.
4. Make notifications idempotent and avoid sending secrets or raw tool arguments.
5. Export audit records without weakening tenant isolation, retention, redaction, or hash-chain verification.
6. Implement one feature at a time. Update API/data-model documentation and migrations when required.
7. Add focused unit and integration tests. Run the repository's required lint, type checks, tests, and container build; report actual results.

## Completion criteria

- Each implemented feature has documented behavior, tenant-scoped authorization, tests, and operational failure handling.
- Billing tests use a provider sandbox or test double; no production payment action occurs without approval.
- Notification retries cannot create duplicate decisions or approvals.
- Audit exports preserve event attribution, redaction rules, and integrity evidence.
- Unimplemented features and missing pilot evidence are listed as blockers, not reported as complete.
