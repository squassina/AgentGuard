# Copilot Prompt — Roadmap Phase 0: Discovery and Protocol Spike

Prepare the discovery artifacts and the smallest technical MCP proxy spike. Read all files in `docs/` and inspect the repository first. Use the confirmed domain model in `GLOSSARY.md` and ADR-013 through ADR-016 when interpreting older documents.

## Work

1. Create a buyer interview guide, design-partner qualification checklist, MCP client/protocol survey, and evidence log template.
2. Separate verified evidence from assumptions. Do not invent interview answers, customer commitments, protocol usage, or willingness to route traffic through AgentGuard.
3. Inspect the existing implementation before building a spike. Reuse an existing safe path when available; do not create a second gateway architecture.
4. Build or document the smallest isolated Streamable HTTP proxy demonstration that can forward one tool call and block it before upstream execution. Use a test upstream and development-only identity.
5. Add a focused automated test proving both allow and deny behavior, including that deny never reaches the upstream.
6. Record protocol/client uncertainties and customer decisions that require human discovery.

## Exit criteria

- The interview and protocol discovery artifacts exist and contain no fabricated findings.
- The technical demonstration proxies a tool call and blocks a denied call before upstream execution.
- Tests reproduce allow and deny outcomes.
- The report lists each external criterion as verified, unverified, or blocked. Never claim the required interviews, design partners, or customer gateway acceptance without evidence.

Stop and recommend a product rethink if verified discovery shows that customers will not route MCP traffic through a cloud gateway.
