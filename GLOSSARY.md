# AgentGuard Domain Model

AgentGuard governs secure MCP tool use across customer tenants. Its domain separates external identities, authorization decisions, human approvals, upstream execution, and audit evidence.

## Tenancy and identity

**Tenant**:
A customer organization and the root ownership and security-isolation boundary for its AgentGuard resources.
_Avoid_: Workspace, Account

**Human identity**:
A person authenticated by a customer workforce identity provider. The identity is keyed by issuer and subject, independently of tenant membership.
_Avoid_: Local user

**Tenant membership**:
The relationship that grants a human identity tenant-specific roles and permissions. One identity can hold memberships in multiple tenants.
_Avoid_: Global role

**Agent**:
An authenticated software principal registered within one Tenant and bound to a verified customer identity. Its authorization does not cross tenant boundaries.
_Avoid_: API key

**Approver**:
A human identity with explicit tenant-scoped authority to decide pending approvals. General administrator authority does not imply approval permission.
_Avoid_: Administrator

## Gateway and authorization

**Upstream**:
A tenant-owned MCP server connection to which AgentGuard routes tool calls.
_Avoid_: Backend

**Tool**:
A capability exposed by an Upstream, identified by its upstream and tool name.
_Avoid_: Action

**Tool call**:
An Agent's request to invoke a Tool through AgentGuard. Its authorization decision and execution outcome are distinct.
_Avoid_: Session authorization

**Policy**:
Tenant-owned deterministic rules that evaluate a tool call's verified identity, route, and explicitly selected normalized inputs.
_Avoid_: Model judgment

**Policy version**:
An immutable published state of a Policy that AgentGuard evaluates for tool calls.
_Avoid_: Mutable policy revision

**Authorization decision**:
The result of Policy evaluation: allow, deny, or require approval.
_Avoid_: Execution outcome

## Approval and evidence

**Approval**:
One-time human authorization for an exact Tool call. It is not a standing grant.
_Avoid_: Access grant

**Audit event**:
An append-only record of a Tool call or security-relevant control-plane transition, attributed to a verified actor.
_Avoid_: Mutable log entry
