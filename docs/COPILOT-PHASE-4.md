# Copilot Prompt — Roadmap Phase 4: Evidence-Gated Expansion

Consider expansion only after the user confirms that product-market evidence meets the roadmap gate. Read all files in `docs/`, inspect current implementation, and preserve unrelated changes. If evidence or approval is missing, produce a readiness assessment and stop before coding.

## Eligible expansion

- Policy templates.
- Approval notifications.
- Additional MCP clients and SDK examples.
- Audit export.
- Usage-based pricing.
- MSP and consultancy partner discovery.

Multiple upstreams per tenant, policy version rollback, agent OAuth/OIDC, and human SSO are MVP requirements under the confirmed domain model. Do not implement them again as Phase 4 work.

## Execution rules

1. Ask the user to select and approve the specific expansion item.
2. Define acceptance criteria and failure handling before implementation.
3. Preserve tenant isolation, least privilege, approval binding, redaction, and audit integrity.
4. Treat commercial interviews, partner commitments, adoption, and revenue as human-verified evidence. Never fabricate them.
5. Do not send notifications, export customer data, contact partners, or incur charges without explicit approval.
6. Implement only the selected item, add focused tests, update documentation, and report exact validation results.

## Completion criteria

- The selected feature is complete and tested without weakening MVP security invariants.
- The report distinguishes shipped functionality from external adoption or commercial outcomes that remain unverified.
