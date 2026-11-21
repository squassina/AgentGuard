# AgentGuard — API and Data Model

**Version:** 0.1 | **Status:** Initial contract; refine during implementation.

## 1. API conventions

- Base path: `/api/v1`
- Gateway path: `/mcp/{route_id}`
- JSON: UTF-8.
- Timestamps: UTC RFC 3339.
- IDs: UUIDv7 or UUIDv4; choose one consistently.
- Every request has `X-Request-ID` or receives a generated correlation ID.
- Tenant context comes from verified auth claims.
- Errors must not reveal whether another tenant's resource exists.

## 2. Control plane endpoints

### Agents
- `POST /api/v1/agents`
- `GET /api/v1/agents`
- `GET /api/v1/agents/{agent_id}`
- `PATCH /api/v1/agents/{agent_id}`
- `POST /api/v1/agents/{agent_id}/credentials`
- `POST /api/v1/agents/{agent_id}/revoke`

### Upstreams
- `POST /api/v1/upstreams`
- `GET /api/v1/upstreams`
- `GET /api/v1/upstreams/{upstream_id}`
- `PATCH /api/v1/upstreams/{upstream_id}`
- `POST /api/v1/upstreams/{upstream_id}/test`
- `POST /api/v1/upstreams/{upstream_id}/rotate-credential`

### Policies
- `POST /api/v1/policies`
- `GET /api/v1/policies`
- `GET /api/v1/policies/{policy_id}`
- `PATCH /api/v1/policies/{policy_id}`
- `POST /api/v1/policies/{policy_id}/activate`
- `POST /api/v1/policies/{policy_id}/disable`

### Approvals
- `GET /api/v1/approvals?status=pending`
- `GET /api/v1/approvals/{approval_id}`
- `POST /api/v1/approvals/{approval_id}/approve`
- `POST /api/v1/approvals/{approval_id}/reject`

### Audit
- `GET /api/v1/audit-events`
- `GET /api/v1/audit-events/{event_id}`
- `GET /api/v1/audit-events/export` (P1)

### System
- `GET /health/live`
- `GET /health/ready`
- `GET /metrics` (internal/authenticated only)

## 3. Gateway contract

- `GET/POST` behavior follows the pinned MCP Streamable HTTP specification and SDK.
- Route binding selects a configured upstream. The client cannot submit an arbitrary upstream URL.
- Every HTTP request is independently authenticated.
- The gateway validates the MCP JSON-RPC envelope and supported method.
- Only explicitly supported methods are advertised.
- `tools/list` returns only tools allowed for discovery, but discovery filtering is not authorization.
- Every `tools/call` is independently authorized even if it was previously listed.
- Upstream calls use a separate upstream credential.
- Do not forward inbound `Authorization`, cookies, or arbitrary hop-by-hop headers.

## 4. Policy schema v1

```yaml
version: 1
name: production-data-protection
status: active
scope:
  agent_ids:
    - "agent_uuid"
  upstream_ids:
    - "upstream_uuid"
  environments:
    - production
rules:
  - id: read-only
    tool: database.read
    effect: allow
  - id: write-approval
    tool: database.write
    effect: require_approval
  - id: delete-deny
    tool: database.delete
    effect: deny
default_effect: deny
```

### Policy semantics
- Exact tool-name match in v1.
- No wildcards in MVP.
- Explicit deny has precedence.
- Multiple matching rules resolve deterministically.
- If more than one non-deny rule matches, `require_approval` takes precedence over `allow`.
- No match means `default_effect`.
- `default_effect` must be `deny` in production.
- Policy activation validates the complete document.
- Every activation creates an immutable policy version.

## 5. Initial relational model

All tenant-owned tables include `tenant_id`. Use foreign keys that include tenant identity where practical, and enable PostgreSQL RLS as defense in depth.

### tenants
- id
- name
- status
- created_at

### users
- id
- external_subject
- email
- display_name
- status
- created_at

### tenant_memberships
- tenant_id
- user_id
- role (`owner`, `admin`, `operator`, `viewer`)
- created_at

### agents
- id
- tenant_id
- name
- owner_user_id nullable
- environment
- status
- metadata JSONB
- created_at
- updated_at

### agent_credentials
- id
- tenant_id
- agent_id
- credential_hash
- credential_prefix
- scopes
- expires_at
- revoked_at
- created_at
- last_used_at

Never store raw credential after creation response.

### upstreams
- id
- tenant_id
- name
- endpoint_url
- transport
- secret_reference
- status
- timeout_ms
- allowed_host
- created_at
- updated_at

### policies
- id
- tenant_id
- name
- status
- active_version
- created_at
- updated_at

### policy_versions
- id
- tenant_id
- policy_id
- version
- document JSONB
- document_hash
- created_by
- created_at
- activated_at

Immutable after activation.

### approvals
- id
- tenant_id
- agent_id
- upstream_id
- tool_name
- arguments_hash
- policy_version_id
- status
- expires_at
- decided_by
- decided_at
- execution_started_at
- execution_completed_at
- result_reference nullable
- created_at

### audit_events
- id
- tenant_id
- request_id
- event_type
- agent_id nullable
- upstream_id nullable
- tool_name nullable
- arguments_hash nullable
- policy_id nullable
- policy_version_id nullable
- decision nullable
- reason_code nullable
- approval_id nullable
- upstream_status nullable
- latency_ms nullable
- previous_hash nullable
- event_hash
- occurred_at

Append-only to application role.

### usage_counters (P1)
- tenant_id
- period_start
- metric
- quantity
- created_at

## 6. Indexes and constraints

- `(tenant_id, created_at)` for audit pagination.
- `(tenant_id, agent_id, status)` for agent lookup.
- `(tenant_id, status, expires_at)` for approvals.
- Unique `(tenant_id, policy_id, version)`.
- Unique credential hash.
- Foreign keys must prevent cross-tenant references.
- Use cursor pagination for audit events.
- JSONB indexes only for fields with demonstrated query needs.

## 7. Error codes

- `AUTHENTICATION_REQUIRED`
- `INVALID_TOKEN`
- `WRONG_AUDIENCE`
- `AGENT_REVOKED`
- `TENANT_ACCESS_DENIED`
- `UPSTREAM_NOT_CONFIGURED`
- `TOOL_NOT_ALLOWED`
- `POLICY_DENIED`
- `APPROVAL_REQUIRED`
- `APPROVAL_EXPIRED`
- `APPROVAL_REPLAYED`
- `POLICY_UNAVAILABLE`
- `UPSTREAM_TIMEOUT`
- `UPSTREAM_FAILURE`
- `REQUEST_TOO_LARGE`
- `UNSUPPORTED_MCP_METHOD`

Return safe public messages; retain detailed internal diagnostics in protected logs.
