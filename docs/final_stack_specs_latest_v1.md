# AI-Artist Final Stack Specs - Latest

## Status

```text
Date: 2026-05-31
Implementation status: all 28 tracker tasks complete
Final validation: 318 passed, 1 skipped, 1 warning
Skipped test: live provider-neutral LLM API smoke test requires deepseek-open-art
Lint: ruff all checks passed
```

## Selected Stack

```text
Agent control plane: OpenClaw workspace files and safety hook contracts
LLM backend: provider-neutral LLM API
Safety service: FastAPI
Policy authority: OPA default-deny policy
Persistence: PostgreSQL query/source/cache/audit schema
Vector store: Qdrant
Object/artifact store: MinIO
Transient state: Redis
Image execution path: ComfyUI adapter behind execution envelope gate
Local orchestration tests: deterministic mock sub-agents
Production readiness: local runbook, env schema, health, backup, restore, retention, contacts
```

## Runtime Services

```text
PostgreSQL 16: query_request_run, source_data_registry, dependency snapshots,
approved_response_cache, audit_event.

Redis 7: queue and transient state placeholder for later async workers.

Qdrant: vector retrieval path for Knowledge Agent tests.

MinIO: artifact/object storage target for generated images and source snapshots.

OPA 0.70.0: default-deny policy for reuse and privileged execution.

FastAPI Safety Service: request canonicalization, classification, local policy
evaluation, execution-envelope signing, audit event recording.
```

## Backend Modules

```text
backend/app.py: FastAPI endpoints.
backend/service.py: canonicalization, classification, local policy gate, execution envelope.
backend/schemas.py: API and SubAgentOutput schemas.
backend/interface_types.py: shared request kind, channel, operation, and audit event type contracts for schemas and runtime modules.
backend/canonical_hash.py: canonical JSON, SHA-256 digests, canonical HMAC signatures, deterministic ID helpers, version tags, and security-review serialization.
backend/request_identity.py: request text normalization, fingerprints, stable request UUIDs, and prefixed runtime trace IDs.
backend/runtime_ids.py: shared runtime UUID and prefixed runtime ID generation.
backend/mapping_utils.py: shared mapping copy and merge helpers for metadata and payload boundaries.
backend/reason_messages.py: shared cache, source-freshness, policy, and execution-envelope reason strings.
backend/subagent_status.py: shared SubAgentOutput status vocabulary, priority, and counting helpers.
backend/review_status.py: shared generated-image review status vocabulary and checks.
backend/critic_rubric.py: shared Critic/Curator rubric categories and pass/fail decision vocabulary.
backend/text_utils.py: shared text tokenization and label normalization.
backend/numeric_utils.py: shared numeric clamps, averages, and vector similarity.
backend/time_utils.py: shared UTC datetime creation and normalization.
backend/payload_fields.py: shared connector payload string-field and nested-object extraction.
backend/response_fields.py: shared provider response field access and shape validation.
backend/url_utils.py: shared URL domain and relative API path validation.
backend/http_methods.py: shared HTTP method vocabulary and normalization for connector boundaries.
backend/operations.py: shared operation constants, classifier terms, and sensitivity rules.
backend/model_coercion.py: shared Pydantic model/dict coercion for adapter and domain boundaries.
backend/adapter_results.py: shared gated adapter result field mapping.
backend/side_effect_audit.py: shared side-effect audit payload and event recording.
backend/secret_redaction.py: shared secret-key and token-shape redaction utilities.
backend/audit.py: in-memory audit repository and recursive secret redaction.
backend/execution_gate.py: shared execution-envelope coercion and validation for gated adapters.
backend/response_cache.py: approved read-only response cache using shared request kind, operation, reason, and time boundaries.
backend/source_freshness.py: dependency snapshot and stale-source checks.
backend/source_ingestion.py: approved local source ingestion with direct canonical hash/version and URL-domain validation boundaries.
backend/connection_settings.py: registry-driven env var names, defaults, aliases, runtime env resolution, and connection settings loader.
backend/llm_api_smoke.py: provider-neutral LLM API configuration and redacted smoke request path.
backend/openclaw_hook.py: pre-tool Safety Service hook.
backend/mock_agent_contracts.py: shared mock sub-agent names and artifact-type vocabulary.
backend/knowledge_contracts.py: shared Knowledge Agent name, retrieval artifact, approved payload flag, collection default, policy note, and summary vocabulary.
backend/orchestrator.py: mock sub-agent routing and synthesis using shared mock-agent contracts.
backend/knowledge.py: deterministic source-cited retrieval using shared Knowledge Agent contracts.
backend/comfyui_adapter.py: execution-envelope-gated image generation adapter.
backend/image_provenance.py: prompt/workflow hashing and provenance records.
backend/critic_curator.py: deterministic image critique rubric.
backend/slack_adapter.py: mocked Slack request/response adapter using shared payload, request identity, and secret-redaction boundaries directly.
backend/publishing.py and backend/publishing_adapter.py: approval-gated publishing path.
backend/publishing_status.py: shared publishing outcome status vocabulary and checks.
backend/github_adapter.py: GitHub write adapter with token isolated to adapter boundary and direct shared URL path validation.
backend/observability.py: telemetry stage/log-level constants, traces, metrics, structured logs, redaction.
backend/security_review.py: deterministic security checklist helpers.
backend/readiness.py: production readiness schema and runbook validators.
```

## Interfaces

```text
GET  /health
POST /v1/requests/canonicalize
POST /v1/requests/classify
POST /v1/policy/evaluate
POST /v1/execution/envelope
POST /v1/audit/events
GET  /v1/audit/events/{correlation_id}
```

## Security Invariants

```text
OPA default allow remains false.
Read-only reuse requires read classification, OPA approval, non-expired cache,
matching requester/policy scope, and unchanged source dependencies.
Write, publish, delete, GitHub write, and image generation are denied until a
valid operation-matching execution envelope exists.
External publish/write paths require human approval.
OpenClaw agents, prompts, logs, audit payloads, and memory files must not
contain raw API keys, OAuth tokens, Slack tokens, GitHub tokens, signing keys, or
private webhook secrets.
Connection names, defaults, secret aliases, target setting fields, and runtime env resolution must be changed through
backend/connection_settings.py before adapter-specific code; the standard LLM
API secret key is `deepseek-open-art`, with `DEEPSEEK_API_KEY` retained only as
a legacy loader alias.
Execution-envelope validation must flow through backend/execution_gate.py before
adapter-specific side-effect logic.
Secret redaction patterns and replacement behavior must flow through
backend/secret_redaction.py before adapter-specific logging or response shaping.
Slack payload parsing, request text normalization, stable request IDs, and
response redaction must call the shared payload, request identity, and
secret-redaction helpers directly at the adapter boundary.
Gated adapter result envelope fields must flow through backend/adapter_results.py
before adapter-specific return dataclasses add extra fields.
Side-effect audit payloads must flow through backend/side_effect_audit.py before
adapter-specific agents persist tool-call audit events.
Canonical JSON, SHA-256 digests, canonical HMAC signatures, deterministic local IDs, version tags, and security-review serialization must
flow through backend/canonical_hash.py before request fingerprints, artifact
hashes, source snapshot versions, signatures, mocked external IDs, or security-review scans are created.
Request text normalization, fingerprint wrappers, stable channel request UUIDs,
and prefixed runtime trace IDs must flow through backend/request_identity.py
before service or adapter specific request identity logic is added.
Runtime UUIDs and prefixed runtime IDs must flow through
backend/runtime_ids.py before service, schema, adapter, orchestration,
freshness, retrieval, or review-specific runtime IDs are created.
Mapping copies and metadata/payload merges must flow through
backend/mapping_utils.py before domain-specific copy or merge logic is added.
Cache, source-freshness, policy, and execution-envelope reason strings must
flow through backend/reason_messages.py before service or cache decision text is
added.
SubAgentOutput status vocabulary, priority, and aggregation must flow through
backend/subagent_status.py before schema or orchestration-specific status
logic is added.
Mock sub-agent names and artifact types must flow through
backend/mock_agent_contracts.py before orchestration-specific agent fixtures are
changed.
Generated image review status vocabulary and checks must flow through
backend/review_status.py before provenance, critic, or publishing-specific
review status logic is added.
Critic/Curator rubric categories and decisions must flow through
backend/critic_rubric.py before scorer-specific rubric logic is added.
Text tokenization and label/tag normalization must flow through
backend/text_utils.py before classifier, retrieval, or rubric-specific token
parsing logic is added.
Numeric clamps, rounded averages, and vector similarity must flow through
backend/numeric_utils.py before orchestration, retrieval, or rubric-specific
scoring logic is added.
UTC datetime creation and normalization must flow directly through backend/time_utils.py
before cache, provenance, execution gate, source freshness, observability, or
future persistence time comparisons are added.
Connector payload required/optional string extraction, tolerant string reads,
and nested-object extraction must flow through
backend/payload_fields.py before adapter-specific payload parsing logic is added.
Provider response object/dict field access and shape validation must flow through
backend/response_fields.py before adapter-specific SDK response parsing logic is
added.
URL/domain extraction and relative API path validation must flow through
backend/url_utils.py before connector-specific URL allowlist or path-safety
logic is added.
HTTP method vocabulary and normalization must flow through backend/http_methods.py
before connector-specific method allowlists are added.
Operation constants, classifier term maps, and sensitive-operation rules must
flow through backend/operations.py before service or adapter operation logic is
added.
Request kind, channel, operation, and audit event type contracts must flow
through backend/interface_types.py before schema, classifier, or audit-specific
literal types are added.
Telemetry stages and log levels must flow through backend/observability.py
constants before service, cache, orchestration, tool, or review-specific
telemetry calls are added.
Publishing outcome status values must flow through backend/publishing_status.py
before publishing agent or side-effect audit status text is added.
Pydantic model/dict coercion at adapter and domain boundaries must flow through
backend/model_coercion.py before direct model validation or one-off validation
wrappers are added.
Generated image provenance stores prompt_hash and workflow_hash, not raw prompt
text in stored records.
```

## Validation Matrix Summary

```text
T01-T02: stack decision and tracker/docs alignment
T03-T07: repository scaffold, compose stack, Safety Service, OPA, PostgreSQL schema
T08-T12: OpenClaw workspace, provider-neutral LLM API config, safety hook, schemas, mock agents
T13-T15: response cache, source freshness, audit log
T16-T19: retrieval, ComfyUI gate, image provenance, critic/curator
T20-T23: Slack, source ingestion, publishing approval, GitHub adapter
T24-T26: unit CI coverage, OpenClaw-to-safety integration, observability
T27-T28: security review and production readiness
```

## Operating Commands

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
docker compose up -d postgres redis qdrant minio opa
docker compose ps
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check .
powershell -ExecutionPolicy Bypass -File .\scripts\run_t24_unit_ci.ps1
```

## Runbooks And Evidence

```text
Production runbook: docs/production_runbook_latest_v1.md
Backend stack setup: docs/backend_stack_setup_latest_v1.md
Task validation matrix: local-ai-agent-system-latest-source/docs/task_validation_matrix_latest_v1.md
Project status: local-ai-agent-system-latest-source/docs/project_status_latest_v1.md
Validation reports: validation_reports/t04 through t28
```
