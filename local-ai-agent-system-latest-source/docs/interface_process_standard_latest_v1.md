# AI-Artist Interface And Process Standard

## Purpose

This document standardizes the implementation handoffs for the OpenClaw +
provider-neutral LLM API AI-Artist system. Every component must speak through explicit
interfaces, produce auditable records, and have a validation test before a task
can be marked done.

## Interface Principles

```text
1. OpenClaw owns agent runtime and tool hooks.
2. The provider-neutral LLM API owns reasoning only; it never receives raw secrets.
3. FastAPI Safety Service owns deterministic safety decisions.
4. Safety Service health status, service name, response payload, and readiness expected-signal text use `backend/health_contracts.py`.
5. Safety Service API metadata and route paths use `backend/api_contracts.py`.
6. OPA owns policy authorization.
7. PostgreSQL owns request, source, cache, and audit records.
8. Qdrant owns vector retrieval.
9. MinIO owns generated files and source snapshots.
10. Redis/Celery/Dagster own background execution state.
11. ComfyUI owns image workflow execution.
12. External write actions require a signed execution envelope whose signature verifies at the shared execution gate.
13. Canonical JSON, hashes, HMAC signatures, deterministic local IDs, source version tags, security-review serialization, direct image-provenance text hashes, deterministic test serialization, and deterministic test text hashes are produced through `backend/canonical_hash.py`.
14. Request text normalization, direct Safety Service canonicalization/classification normalization, fingerprints, stable channel UUIDs, and prefixed runtime trace IDs are produced through `backend/request_identity.py`.
15. Request metadata defaults, default request channel, request envelope field names, RequestMetadata workspace/agent mapping, canonical request fingerprint fields, and canonicalization observability fields use `backend/request_metadata_contracts.py` and `backend/request_metadata.py`.
15a. Safety Service canonicalization, classification, and policy observability event/message/tag/field shapes use `backend/service_observability_contracts.py`.
15b. Execution-envelope-id, client-response, operation, target, request-id, correlation-id, status, request-kind, requester/policy scope, allow, human-approval, reason, and policy-version field names use `backend/runtime_field_contracts.py` before service observability, OpenClaw tool telemetry, observability trace fallback metadata, execution-envelope signature payloads, adapter result payloads, audit response payloads, Slack local request scope/request-id/result payloads, publishing response payloads, or side-effect audit payload shapes are changed.
16. Default requester, policy, publishing actor, and publishing policy scopes use `backend/request_scope_contracts.py`.
17. Runtime UUIDs and prefixed runtime IDs use `backend/runtime_ids.py`.
18. Mapping copies and metadata/payload merges use `backend/mapping_utils.py`.
19. Cache, source-freshness, policy, and execution-envelope reason strings use `backend/reason_messages.py`.
19a. Local default-deny policy versioning, execution-envelope signing key, runtime-field-backed signature payload/signing/verification helpers, and execution-envelope TTL use `backend/policy_contracts.py` and `backend/runtime_field_contracts.py`.
19b. Source freshness schema defaults, unchanged-source checks, and unchanged-source payload construction use `backend/source_freshness_contracts.py`.
20. Sub-agent status vocabulary, priority, and aggregation use `backend/subagent_status.py`.
21. Sub-agent output construction, payload field names, and model coercion use `backend/subagent_output_contracts.py`, with task-id/status field names reused from `backend/runtime_field_contracts.py`.
22. Mock sub-agent names, artifact types, output text, error text, simulation metadata lookup, synthesis text, orchestration telemetry events/messages/metrics, and telemetry field/tag shapes use `backend/mock_agent_contracts.py`, with generic task/requester/policy/status fields reused from `backend/runtime_field_contracts.py`.
23. Generated-image review status vocabulary and checks use `backend/review_status.py`.
24. Critic/Curator rubric categories, decisions, score bounds, pass thresholds, scoring weights, publication penalties, and score helpers use `backend/critic_rubric.py`.
25. Text tokenization, direct Safety Service classifier token parsing, label/tag normalization, and contextual snippets use `backend/text_utils.py`.
26. Numeric clamps, rounded averages, vector similarity, positive-integer checks, and zero-magnitude checks use `backend/numeric_utils.py` directly at scoring boundaries.
27. Connection names, target setting fields, defaults, secret aliases, endpoint URL composition, env-example rendering/parsing/validation, runtime env resolution, runtime secret resolution, connection error messages, and env-access guards use `backend/connection_settings.py`.
28. LLM smoke request prompts, reasoning effort, thinking mode, timeout, chat request field names, role vocabulary, request/result payload construction, runtime secret lookup, and redacted request recording use `backend/llm_api_contracts.py` and `backend/llm_api_smoke.py`.
29. Cache, provenance, execution-envelope, source freshness, observability, and persistence timestamps use `backend/time_utils.py` directly for UTC creation and normalization.
30. Connector payload string-field extraction, tolerant string reads, and nested object extraction use `backend/payload_fields.py`.
31. Provider response object/dict field access, first-choice message content extraction, shape validation, and response validation messages use `backend/response_fields.py`.
31a. Response-cache reuse telemetry event, message, metric tags, and structured fields use `backend/response_cache_contracts.py`, with generic operation/request-kind/reason fields reused from `backend/runtime_field_contracts.py`.
32. Connector URL/domain, relative API path validation, and URL validation messages use `backend/url_utils.py`.
33. Connector HTTP method vocabulary, normalization, and validation messages use `backend/http_methods.py`.
34. Operation constants, classification term maps, and sensitivity rules use `backend/operations.py`.
35. Classifier confidence and reason formatting use `backend/classification_contracts.py`.
36. Request kind, channel, operation, and audit event type contracts use `backend/interface_types.py`, including OpenClaw pre-tool approval checks.
36a. OpenClaw tool policy metadata, redaction, metric tags, and telemetry fields use `backend/openclaw_contracts.py`.
37. Telemetry stages, log levels, default metric values, metric-name constants/formatting, trace-id fallback formatting, and event-message formatting use `backend/observability.py`.
38. Publishing outcome statuses use `backend/publishing_status.py`.
38a. Local publishing dry-run response fields, deterministic ID material, and status/target aliases use `backend/publishing_contracts.py`, with status/target field spellings reused from `backend/runtime_field_contracts.py`.
39. Pydantic model/dict coercion and validation messages at service, adapter, and domain boundaries call `backend/model_coercion.py` directly.
40. Knowledge Agent names, retrieval artifact types, vector payload fields/shape, vector payload write/read helpers, approved-source payload flags, collection defaults, embedding defaults, stable token-index hashing, vector-search limit/sort behavior, result-score cutoff/precision, policy notes, and summary vocabulary use `backend/knowledge_contracts.py`.
41. Observability fields and metric tags use `backend/audit.py` redacted mapping helpers for telemetry-safe dict payloads.
41a. Audit actor/policy scope payload field names, accepted response flag, and audit response payload shape use `backend/audit_contracts.py`, with generic policy-scope spelling reused from `backend/runtime_field_contracts.py`.
42. ComfyUI generated-image URI conventions, response image field names, response image validation messages, and response image storage references use `backend/comfyui_contracts.py`.
43. Source registry missing-row messages, dependency-role defaults, empty change-sequence defaults, and initial change-sequence defaults use `backend/source_registry_contracts.py`.
44. Execution-envelope validation failure, signature failure, and required-envelope messages use `backend/execution_gate_messages.py`.
45. Secret-like value detection, assignment scanning, structured unredacted-secret checks, and redaction use `backend/secret_redaction.py`.
46. Reviewable text-file suffixes and recursive scanner discovery use `backend/file_scanning.py`.
47. Markdown heading extraction for documentation validators uses `backend/markdown_utils.py`.
48. Optional source registry row lookup uses `SourceFreshnessRegistry.find_source` and `SourceFreshnessRegistry.find_source_by_id`.
49. Publishing side-effect audit operation values use `backend/operations.py`, and side-effect audit event types use `backend/interface_types.py`.
49a. Side-effect audit payload field names use `backend/runtime_field_contracts.py` and `backend/side_effect_audit_contracts.py`.
50. Gated adapter operation values use `backend/operations.py` directly.
51. Gated adapter action and target labels use `backend/adapter_gate_contracts.py` before execution-envelope message construction.
51a. Gated adapter result envelope IDs, request IDs, operation, target, and client response field names use `backend/adapter_results.py`, with generic execution-envelope/client-response/request/operation/target field names reused from `backend/runtime_field_contracts.py`, before adapter return dataclasses or side-effect audit payloads change.
51. Slack source labels, inbound event field names, requester/policy scopes, runtime-field-backed local requester/policy/request-id and client-response fields, local-request payloads, outbound payloads, post-result payloads, adapter validation messages, and token-purpose text use `backend/slack_contracts.py`.
52. GitHub adapter action labels, validation messages, token-purpose text, token-required message routing, and explicit/env token lookup use `backend/github_contracts.py`, `backend/connection_settings.py`, and `backend/adapter_secrets.py`; standard runtime secret setting-name lookup is derived inside the connection registry.
53. Source ingestion approved-domain defaults, rejection messages, registry metadata keys, and registry metadata payload shape use `backend/source_ingestion_contracts.py`.
54. Production readiness service URLs, `.env.example` rendering, and health/backup/restore endpoint commands use `backend/connection_settings.py`.
55. Production readiness Docker Compose, curl, and MinIO command strings, OPA/test process argument lists, test process invocations, and delimited process-output parsers use `backend/shell_commands.py`.
56. Production readiness backup directories, container dump paths, and MinIO aliases use `backend/readiness_paths.py`.
57. Production readiness env, runbook, and command validation detail messages use `backend/readiness.py`.
58. Repository artifact paths, repo-root resolution, workspace paths/text reads, backend module discovery, source-text reads, and source-inspection file reads for Compose, env, runbook, OPA policy, PostgreSQL schema, workspace, and backend module files use `backend/repo_paths.py`.
59. Repo-wide validation tests that scan project, backend, or test sources use `tests/path_helpers.py` for project-root resolution, project text reads, backend source reads, test source reads, and source iteration.
60. Security review finding surfaces, messages, probe event/trace IDs, policy default-deny pattern, review target formatting, and prompt-hash field checks use `backend/security_review_contracts.py`.
61. Gated-adapter and policy-path tests use `tests/execution_envelope_helpers.py` for approved, unapproved, unchanged-source, and stale-source execution-envelope setup.
62. Cache, freshness, observability, and Safety Service policy-path tests use `tests/policy_request_helpers.py` for standard `PolicyEvaluateRequest` setup.
63. LLM, Slack, GitHub, and connection-settings tests use `tests/connection_env_helpers.py` for standard env maps and test secret values.
64. Audit, security-review, secret-redaction, and side-effect audit tests use `tests/secret_test_helpers.py` for standard secret-bearing payloads and redaction assertions.
65. OpenClaw hook and observability tests use `tests/tool_call_helpers.py` for standard `ToolCallRequest` setup.
66. Cache, source-freshness, and observability tests use `tests/cache_entry_helpers.py` for standard `ApprovedResponseCacheEntry` setup.
```

## Standard Request Envelope

All runtime paths begin with a normalized request envelope.

```json
{
  "request_id": "uuid",
  "request_text": "string",
  "request_kind": "read|action|mixed",
  "request_fingerprint": "sha256-canonical-request",
  "requester_scope": "user-or-channel-scope",
  "policy_scope": "policy-scope",
  "channel": "slack|cli|web|job",
  "created_at": "iso-8601",
  "metadata": {
    "workspace": "ai-artist-main",
    "agent": "ai-artist-main"
  }
}
```

## Component Interfaces

### OpenClaw Gateway To FastAPI Safety Service

```text
POST /v1/requests/canonicalize
POST /v1/requests/classify
POST /v1/policy/evaluate
POST /v1/reuse/check
POST /v1/execution/envelope
POST /v1/audit/events
```

Rules:

- OpenClaw sends task context and request metadata only.
- OpenClaw never forwards API keys, OAuth tokens, signing keys, or private
  webhooks to the configured LLM API.
- Runtime env and connection settings are resolved through the shared
  connection settings helper before adapters or live tests read provider
  credentials.
- `.env.example` must match the shared connection settings registry rendering, parsing, and validation helpers.
- Readiness health, backup, and restore endpoint commands compose service URLs
  through the shared connection settings helper.
- Readiness Docker Compose, curl, and MinIO command syntax, OPA/test process
  argument lists, test process invocations, and delimited process-output parsers are built or executed
  through the shared shell command helper.
- Readiness backup directories, container dump paths, and MinIO aliases use the
  shared readiness path contract.
- Readiness env, runbook, and command validation detail messages use the shared
  readiness message helpers.
- Repository artifact paths, repo-root resolution, workspace paths/text reads,
  backend module discovery, source-text reads, and source-inspection file reads
  use the shared repo path contract before runtime review checks, scaffold
  validators, or contract guards read checked-in files.
- Repo-wide validation tests that scan project, backend, or test sources use
  shared test path helpers instead of local root resolution, local source reads,
  or test-module glob loops.
- LLM, Slack, GitHub, connection-settings, and future connection tests use
  `tests/connection_env_helpers.py` instead of repeating env-var maps or test
  secret constants locally.
- Audit, security-review, secret-redaction, side-effect audit, and future
  redaction tests use `tests/secret_test_helpers.py` instead of repeating
  token-shaped payloads or redaction assertion helpers locally.
- OpenClaw hook, observability, and future tool-stage tests use
  `tests/tool_call_helpers.py` instead of constructing standard
  `ToolCallRequest` fixtures directly.
- Cache, source freshness, observability, Safety Service unit, and future
  policy-path tests use `tests/policy_request_helpers.py` instead of
  constructing standard `PolicyEvaluateRequest` fixtures directly.
- Cache, source freshness, observability, and future cache-path tests use
  `tests/cache_entry_helpers.py` instead of constructing standard
  `ApprovedResponseCacheEntry` fixtures directly.
- Gated-adapter and policy-path tests that need approved, unapproved, unchanged-source, or stale-source execution envelopes use
  `tests/execution_envelope_helpers.py` instead of constructing
  `ExecutionEnvelopeRequest` directly in adapter-specific, policy-contract,
  Safety Service unit, or publishing-agent test modules.
- Tool hooks must call `/v1/execution/envelope` before external writes.

### FastAPI Safety Service To OPA

```text
POST /v1/data/ai_artist/allow
```

Policy input shape:

```json
{
  "request_id": "uuid",
  "request_kind": "read|action|mixed",
  "operation": "reuse|read|write|publish|delete|github_write|image_generate",
  "requester_scope": "string",
  "policy_scope": "string",
  "requires_human_approval": true,
  "source_freshness": {
    "all_required_sources_unchanged": true,
    "changed_source_count": 0
  }
}
```

OPA response shape:

```json
{
  "allow": true,
  "reason": "string",
  "requires_human_approval": false,
  "policy_version": "string"
}
```

### OpenClaw Runtime To Sub-Agents

Sub-agents receive bounded task payloads and return `SubAgentOutput`.

```json
{
  "task_id": "uuid",
  "parent_request_id": "uuid",
  "agent_name": "social-scout|image-gen|critic-curator|knowledge|publishing|audit",
  "task_type": "research|generate_image|critique|retrieve|publish|audit",
  "input": {},
  "constraints": {
    "may_write_external": false,
    "may_use_network": false,
    "max_runtime_seconds": 120
  }
}
```

```json
{
  "task_id": "uuid",
  "agent_name": "string",
  "status": "ok|needs_retry|blocked|failed",
  "summary": "string",
  "artifacts": [],
  "sources": [],
  "policy_notes": [],
  "confidence": 0.0,
  "errors": []
}
```

### Image Generation Interface

OpenClaw calls the ComfyUI adapter only after the execution policy gate allows
image generation.

```json
{
  "execution_envelope_id": "uuid",
  "prompt": "string",
  "negative_prompt": "string",
  "workflow_name": "flux-dev-default|sdxl-default",
  "model": "string",
  "seed": 12345,
  "width": 1024,
  "height": 1024,
  "source_refs": [],
  "review_required": true
}
```

Output:

```json
{
  "artifact_id": "uuid",
  "storage_uri": "minio://bucket/key",
  "preview_uri": "minio://bucket/preview-key",
  "workflow_hash": "sha256",
  "prompt_hash": "sha256",
  "seed": 12345,
  "review_status": "pending|approved|rejected"
}
```

## Standard Delivery Process

```text
1. Intake
   - OpenClaw receives the request and loads workspace context.
   - Channel adapters and audit records validate connector strings and nested payload objects through the shared payload-field helper.

2. Normalize
   - Safety Service canonicalizes request text and builds a stable fingerprint.
   - Safety Service health responses and readiness expectations use the shared health contract.
   - Request metadata workspace/agent fields, canonical request fingerprint fields, and canonicalization observability fields use the shared metadata helper.
   - Request metadata defaults, default channel, request envelope field names, and fingerprint field names use the shared metadata contract before schema or telemetry changes.
   - Safety Service request and policy telemetry shapes use the shared service-observability contract helper.
   - Runtime policy/telemetry/audit field names use the shared runtime field contract before service, OpenClaw, observability trace fallback, execution-envelope signature, adapter result, response-cache telemetry, audit response, audit policy-scope extraction, sub-agent output construction, mock orchestration telemetry, Slack local request/result, publishing response, or side-effect audit payload shapes are changed.
   - Canonical JSON, SHA-256 digest creation, HMAC signing, and security-review serialization flow through the shared hash helper.
   - Channel adapters and tool hooks use the shared request identity helper for text normalization, stable event ids, and prefixed trace ids.
   - Slack adapter payload parsing, request identity, local request/outbound payload construction, secret redaction, and runtime token lookup call the shared helpers directly at the adapter boundary.
   - Slack source labels, inbound event fields, runtime-field-backed local requester/policy/request-id and client-response fields, outbound payload fields, post-result payloads, and adapter validation messages use the shared Slack contract before adapter errors are raised.
   - Runtime UUID creation uses the shared runtime ID helper.
   - Metadata and payload copies use the shared mapping helper.

3. Classify
   - Safety Service classifies request as read, action, or mixed.
   - Operation inference and read/action term maps come from the shared operation registry.
   - Classifier confidence and reasons use the shared classification response contract.
   - Classifier token parsing uses the shared text utility helper.

4. Policy Check
   - Safety Service asks OPA whether processing may continue.
   - Sensitive-operation checks come from the shared operation registry before envelopes are issued.
   - Policy responses, execution-envelope policy versions, runtime-field-backed signing payload, signing key, signature verification, and expiry TTL use the shared policy and runtime field contracts.

5. Reuse Decision
   - Read-only repeat requests check approved cache and source freshness.
   - Fresh source snapshot defaults, unchanged-source checks, and unchanged-source payload construction come from the shared source-freshness contract.
   - Cache, source-freshness, policy, and execution-envelope decision text uses the shared reason-message helper.
   - Cache replay and OpenClaw pre-tool approval request-kind checks use shared interface and operation constants.
   - Cache reuse telemetry event, message, metric tags, and structured fields use the shared response-cache contract helper, with operation/request-kind/reason field names reused from the runtime field contract.
   - OpenClaw tool policy metadata and redacted tool arguments use the shared OpenClaw contract helper.
   - Source ingestion validates absolute HTTP(S) source domains through the shared URL helper.
   - Source ingestion approved-domain defaults, rejection messages, registry metadata keys, and registry metadata payload shape use the shared source-ingestion contract.
   - Source snapshot content hashes and version tags use the shared canonical hash helper.
   - Source ingestion calls shared hash/version helpers directly before registry and snapshot writes.
   - Source registry lookup failures, dependency roles, and initial change sequences use shared source registry contracts.
   - Source ingestion checks for existing registry rows through the source registry optional lookup API.

6. Orchestrate
   - Fresh or changed requests route through OpenClaw sub-agents.
   - Sub-agent outputs are constructed through the shared output contract helper and its exported payload field constants.
   - Mock orchestration agent names, artifact types, simulation metadata lookup, synthesis text, and telemetry field/tag shapes use the shared mock-agent contract, with task/requester/policy/status field names reused from the runtime field contract.
   - Retrieval embeddings, snippets, and rubric labels use shared text tokenization and label normalization.
   - Retrieval vector payload fields/shape, vector payload write/read helpers, embedding defaults, stable token-index hashing, vector-search limit/sort behavior, positive-hit filtering, and score precision use shared Knowledge Agent contracts.
   - Knowledge retrieval result snippets use the shared contextual snippet helper.
   - Retrieval vector similarity, embedding dimension validation, zero-vector handling, rubric helper clamping, and orchestration confidence use shared numeric helpers.
   - Critic/Curator score bounds, score conversion, pass thresholds, and publication penalties call the shared rubric scoring contracts directly without local wrapper functions.

7. Validate
   - Runtime validates `SubAgentOutput`, compares results, retries if needed,
     and synthesizes one response.
   - Knowledge and mock sub-agent output coercion uses the shared sub-agent output constructor, with task-id/status field spellings reused from the runtime field contract.
   - Domain and adapter inputs and structured outputs coerce model-or-dict payloads through the shared model coercion helper.
   - Provider SDK object-or-dict responses are read through the shared response-field helper.
   - Connector HTTP methods are normalized through the shared HTTP method helper.
   - GitHub adapter labels, API validation messages, token-purpose text, and explicit/env token resolution use shared GitHub/connection/adapter-secret contracts before adapter errors are raised.

8. Execution Gate
   - Any external write, publish, GitHub write, deletion, or image generation
     receives a signed execution envelope.
   - Gated adapters pass shared operation constants and shared action/target labels directly into the execution gate.
   - Gated adapter result field vocabulary uses the shared adapter result and runtime field contracts before adapter return or side-effect audit payload fields are changed.
   - Envelope validation and signature failure messages use the shared execution-gate message contract.
   - Execution-envelope signatures are created and verified through the shared policy contract, backed by the canonical HMAC helper.
   - Envelope issue times, cache checks, source timestamps, telemetry timestamps, and expiry comparisons use direct shared UTC creation and normalization.
   - OpenClaw tool metric tags, preflight fields, decision fields, and executed fields use the shared OpenClaw contract helper.
   - Connector API paths are normalized and rejected for absolute URLs, traversal,
     backslashes, and control characters before token reads.

9. Deliver
   - Output Tool Agent sends the response or executes the approved action.

10. Audit
   - Every request, cache reuse, policy decision, execution envelope, tool call,
     and artifact is recorded.
   - Security review and scanner paths detect secret-like values through the shared secret-redaction boundary.
   - Security review and scanner paths discover reviewable workspace files through the shared file-scanning boundary.
   - Security review finding surfaces, messages, probe event/trace IDs, policy default-deny checks, review target formatting, and prompt-hash field checks use the shared security-review contract boundary.
   - Audit record actor/policy scope extraction, audit response payloads, and side-effect audit payload fields use the shared audit scope and response contracts, with policy-scope spelling reused from the runtime field contract.
   - Publishing side-effect audit events use the shared publish operation, payload field-name, and audit event type constants.
   - Side-effect audit operation, target, status, reason, and policy-scope payload fields use the shared runtime field contract.
   - Side-effect audit execution-envelope and client-response payload fields use the shared adapter result field contract.
   - Publishing audit actor and policy scopes use the shared request-scope contract.
   - Local publishing dry-run responses, deterministic IDs, and status/target fields use the shared publishing contract helper and runtime field contract.
```

## Definition Of Done

A task is done only when:

- its interface contract is documented or implemented;
- its validation test passes;
- failure behavior is defined;
- secrets are absent from prompts, logs, memory, and audit payloads;
- audit events are emitted for policy-sensitive paths;
- the project tracker records the validation test and result.
- `Status` is set to the final result and `Finished` contains the completion
  date for completed work.
- documentation validators parse Markdown headings through the shared Markdown
  utility boundary.

## Tracker Columns

```text
Status
  Current validation state: Ausstehend, In Arbeit, Bestanden, Blockiert, or Failed.

Finished
  Completion date in YYYY-MM-DD format. Empty until validation passes.
```
