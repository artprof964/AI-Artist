# AI-Artist Final Stack Specs - Latest

## Status

```text
Date: 2026-05-31
Implementation status: all 28 tracker tasks complete
Final validation: 404 passed, 1 skipped, 1 warning
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
backend/health_contracts.py: shared Safety Service health status, service name, response payload, and readiness signal.
backend/classification_contracts.py: shared classifier confidence and reason formatting.
backend/interface_types.py: shared request kind, channel, operation, and audit event type contracts for schemas and runtime modules.
backend/canonical_hash.py: canonical JSON, SHA-256 digests, canonical HMAC signatures, deterministic ID helpers, version tags, security-review serialization, direct image-provenance text hashes, deterministic test serialization, and deterministic test text hashes.
backend/request_identity.py: request text normalization, direct Safety Service canonicalization/classification normalization, fingerprints, stable request UUIDs, and prefixed runtime trace IDs.
backend/request_metadata.py: shared RequestMetadata workspace/agent mapping for fingerprints and observability fields.
backend/runtime_ids.py: shared runtime UUID and prefixed runtime ID generation.
backend/mapping_utils.py: shared mapping copy and merge helpers for metadata and payload boundaries.
backend/reason_messages.py: shared cache, source-freshness, policy, and execution-envelope reason strings.
backend/subagent_status.py: shared SubAgentOutput status vocabulary, priority, and counting helpers.
backend/subagent_output_contracts.py: shared SubAgentOutput construction and model-coercion boundary.
backend/review_status.py: shared generated-image review status vocabulary and checks.
backend/critic_rubric.py: shared Critic/Curator rubric categories and pass/fail decision vocabulary.
backend/text_utils.py: shared text tokenization, direct Safety Service classifier token parsing, label normalization, and contextual snippets.
backend/markdown_utils.py: shared Markdown heading extraction for documentation validators.
backend/numeric_utils.py: shared numeric clamps, averages, and vector similarity.
backend/time_utils.py: shared UTC datetime creation and normalization for runtime code and tests.
backend/payload_fields.py: shared connector payload string-field and nested-object extraction.
backend/response_fields.py: shared provider response field access, first-choice message parsing, and shape validation.
backend/url_utils.py: shared URL domain and relative API path validation.
backend/http_methods.py: shared HTTP method vocabulary and normalization for connector boundaries.
backend/file_scanning.py: shared reviewable text-file suffixes and recursive scanner file discovery.
backend/operations.py: shared operation constants, classifier terms, and sensitivity rules.
backend/model_coercion.py: shared Pydantic model/dict coercion for adapter and domain boundaries.
backend/adapter_results.py: shared gated adapter result field mapping.
backend/side_effect_audit.py: shared side-effect audit payload and event recording.
backend/secret_redaction.py: shared secret-key detection, token-shape detection, assignment-pattern detection, and redaction utilities.
backend/comfyui_contracts.py: shared ComfyUI generated-image URI convention, response image validation messages, and response-image storage reference helper.
backend/source_registry_contracts.py: shared source registry missing-row message contract.
backend/source_ingestion_contracts.py: shared source ingestion approved-domain defaults and rejection message contracts.
backend/slack_contracts.py: shared Slack source label, validation message contracts, and token-purpose text.
backend/github_contracts.py: shared GitHub adapter action labels, validation messages, and token-purpose text.
backend/audit.py: in-memory audit repository, recursive secret redaction, and redacted mapping helper for telemetry/audit payloads.
backend/execution_gate_messages.py: shared execution-envelope validation failure and required-envelope message contracts.
backend/execution_gate.py: shared execution-envelope coercion and validation for gated adapters.
backend/response_cache.py: approved read-only response cache using shared request kind, operation, reason, and time boundaries.
backend/source_freshness.py: dependency snapshot, stale-source checks, and optional source registry lookup.
backend/source_ingestion.py: approved local source ingestion with direct canonical hash/version and URL-domain validation boundaries.
backend/connection_settings.py: registry-driven env var names, defaults, aliases, runtime env resolution, runtime secret resolution and guards, endpoint URL composition, env-example rendering, and connection settings loader.
backend/shell_commands.py: shared shell command construction for Docker Compose, curl, and MinIO command definitions plus subprocess execution defaults and delimited process-output parsing.
backend/readiness_paths.py: shared production readiness backup paths, container dump path, and MinIO source alias.
backend/repo_paths.py: shared repository artifact paths, repo-root resolution, workspace paths/text reads, backend module discovery, source-text readers, and source-inspection file reads for Compose, env, runbook, OPA policy, PostgreSQL schema, and backend module files.
backend/llm_api_smoke.py: provider-neutral LLM API configuration and redacted smoke request path.
backend/openclaw_hook.py: pre-tool Safety Service hook using direct shared secret-redaction boundary.
backend/mock_agent_contracts.py: shared mock sub-agent names, artifact types, output text, error text, synthesis text, and orchestration telemetry contracts.
backend/knowledge_contracts.py: shared Knowledge Agent name, retrieval artifact, approved payload flag, collection default, policy note, and summary vocabulary.
backend/orchestrator.py: mock sub-agent routing and synthesis using shared mock-agent contracts.
backend/knowledge.py: deterministic source-cited retrieval using shared Knowledge Agent contracts.
backend/comfyui_adapter.py: execution-envelope-gated image generation adapter using direct shared operation constants.
backend/image_provenance.py: prompt/workflow hashing and provenance records using shared ComfyUI image URI contracts and direct model-coercion boundary.
backend/critic_curator.py: deterministic image critique rubric using direct model-coercion and numeric-clamp boundaries.
backend/slack_adapter.py: mocked Slack request/response adapter using shared payload, request identity, secret-redaction, and runtime secret boundaries directly.
backend/publishing.py and backend/publishing_adapter.py: approval-gated publishing path using direct shared operation constants.
backend/publishing_status.py: shared publishing outcome status vocabulary and checks.
backend/github_adapter.py: GitHub write adapter with token isolated to adapter boundary and direct shared operation and URL path validation.
backend/observability.py: telemetry stage/log-level constants, traces, metrics, and structured logs using shared audit redacted-mapping boundary.
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
Safety Service health status, service name, response payload, and readiness
expected-signal text must flow through backend/health_contracts.py before
endpoint, schema, or runbook readiness health-check logic is changed.
Connection names, defaults, secret aliases, target setting fields, endpoint URL
composition, env-example rendering, runtime env resolution, runtime secret resolution, and env-access guards must be changed through
backend/connection_settings.py before adapter-specific code; the standard LLM
API secret key is `deepseek-open-art`, with `DEEPSEEK_API_KEY` retained only as
a legacy loader alias.
Shell command strings for Docker Compose, curl, and MinIO readiness commands,
subprocess execution defaults, and delimited process-output parsing must flow
through backend/shell_commands.py before production readiness command
definitions, test process invocations, or migration output parsers are changed.
Production readiness backup directories, container dump paths, and MinIO source
aliases must flow through backend/readiness_paths.py before runbook or command
definitions are changed.
Repository artifact paths, repo-root resolution, workspace paths/text reads,
backend module discovery, source-text reads, and source-inspection file reads
must flow through backend/repo_paths.py before runtime review checks, scaffold
tests, contract guards, or documentation validators reference Compose, env,
runbook, OPA policy, PostgreSQL schema, workspace, or backend module files.
Execution-envelope validation must flow through backend/execution_gate.py before
adapter-specific side-effect logic.
Execution-envelope validation failure and required-envelope messages must flow through
backend/execution_gate_messages.py before gated adapters expose envelope errors.
Secret detection patterns, assignment scanning, and replacement behavior must
flow through backend/secret_redaction.py before adapter-specific logging,
response shaping, security review, or future scanner logic.
OpenClaw policy metadata redaction must call `backend/secret_redaction.py`
directly when preparing Safety Service policy requests.
Slack payload parsing, request text normalization, stable request IDs, and
response redaction must call the shared payload, request identity, and
secret-redaction helpers directly at the adapter boundary.
Slack source labels and adapter validation messages must flow through
backend/slack_contracts.py before Slack event parsing or response formatting
raises adapter errors.
Gated adapter result envelope fields must flow through backend/adapter_results.py
before adapter-specific return dataclasses add extra fields.
Side-effect audit payloads must flow through backend/side_effect_audit.py before
adapter-specific agents persist tool-call audit events.
Canonical JSON, SHA-256 digests, canonical HMAC signatures, deterministic local IDs, version tags, security-review serialization, direct image-provenance text hashes, deterministic test serialization, and deterministic test text hashes must
flow through backend/canonical_hash.py before request fingerprints, artifact
hashes, image provenance hashes, source snapshot versions, signatures, mocked external IDs, security-review scans, deterministic test serializations, or deterministic test text hashes are created.
Request text normalization, fingerprint wrappers, stable channel request UUIDs,
and prefixed runtime trace IDs must flow through backend/request_identity.py
before service or adapter specific request identity logic is added.
Safety Service canonicalization and classification must call
backend/request_identity.py directly for request text normalization.
RequestMetadata workspace/agent mapping must flow through
backend/request_metadata.py before service fingerprinting, observability metric
tags, or structured observability fields are built.
Runtime UUIDs and prefixed runtime IDs must flow through
backend/runtime_ids.py before service, schema, adapter, orchestration,
freshness, retrieval, or review-specific runtime IDs are created.
Mapping copies and metadata/payload merges must flow through
backend/mapping_utils.py before domain-specific copy or merge logic is added.
Cache, source-freshness, policy, and execution-envelope reason strings must
flow through backend/reason_messages.py before service or cache decision text is
added.
Source registry missing-row messages must flow through
backend/source_registry_contracts.py before source freshness or future
persistence adapters raise missing-row errors.
Existing source registry row checks must call SourceFreshnessRegistry.find_source
before ingestion or future persistence code handles optional source rows.
SubAgentOutput status vocabulary, priority, and aggregation must flow through
backend/subagent_status.py before schema or orchestration-specific status
logic is added.
SubAgentOutput construction and model coercion must flow through
backend/subagent_output_contracts.py before Knowledge retrieval, mock
orchestration, or future sub-agent adapters return structured agent outputs.
Mock sub-agent names, artifact types, output text, error text, synthesis text,
and orchestration telemetry must flow through backend/mock_agent_contracts.py
before orchestration-specific agent fixtures are changed.
Generated image review status vocabulary and checks must flow through
backend/review_status.py before provenance, critic, or publishing-specific
review status logic is added.
Critic/Curator rubric categories and decisions must flow through
backend/critic_rubric.py before scorer-specific rubric logic is added.
Text tokenization, label/tag normalization, and contextual snippets must flow through
backend/text_utils.py before classifier, retrieval, or rubric-specific token
parsing logic is added.
Safety Service classification must call backend/text_utils.py directly for
classifier token parsing.
Markdown heading extraction must flow through backend/markdown_utils.py before
readiness or future documentation validators inspect section headings.
Numeric clamps, rounded averages, and vector similarity must flow through
backend/numeric_utils.py before orchestration, retrieval, or rubric-specific
scoring logic is added.
Critic/Curator rubric score bounds must call backend/numeric_utils.py directly
before category or publication-readiness scores are emitted.
UTC datetime creation and normalization must flow directly through backend/time_utils.py
before cache, provenance, execution gate, source freshness, observability, or
future persistence time comparisons are added.
Tests that need current UTC time must call backend/time_utils.py instead of
calling datetime.now(timezone.utc) directly.
Connector payload required/optional string extraction, tolerant string reads,
and nested-object extraction must flow through
backend/payload_fields.py before adapter-specific payload parsing logic is added.
Provider response object/dict field access and shape validation must flow through
backend/response_fields.py before adapter-specific SDK response parsing logic is
added.
Source ingestion approved-domain defaults and rejection text must flow through
backend/source_ingestion_contracts.py before ingestion allowlists or rejection
messages are changed.
URL/domain extraction and relative API path validation must flow through
backend/url_utils.py before connector-specific URL allowlist or path-safety
logic is added.
HTTP method vocabulary and normalization must flow through backend/http_methods.py
before connector-specific method allowlists are added.
GitHub adapter action labels, target labels, API validation messages, and token
purpose text must flow through backend/github_contracts.py before GitHub adapter
errors are raised.
Reviewable text-file suffixes and recursive scanner discovery must flow through
backend/file_scanning.py before security review or future scanner paths inspect
workspace files.
Operation constants, classifier term maps, and sensitive-operation rules must
flow through backend/operations.py before service or adapter operation logic is
added.
Classifier confidence and reason formatting must flow through
backend/classification_contracts.py before `ClassifyResponse` fields are
emitted.
Publishing side-effect audit operation values must call backend/operations.py
directly before audit events are recorded.
Gated adapter operation values must call backend/operations.py directly before
execution-envelope validation.
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
