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
5. OPA owns policy authorization.
6. PostgreSQL owns request, source, cache, and audit records.
7. Qdrant owns vector retrieval.
8. MinIO owns generated files and source snapshots.
9. Redis/Celery/Dagster own background execution state.
10. ComfyUI owns image workflow execution.
11. External write actions require a signed execution envelope.
12. Canonical JSON, hashes, HMAC signatures, deterministic local IDs, source version tags, and security-review serialization are produced through `backend/canonical_hash.py`.
13. Request text normalization, fingerprints, stable channel UUIDs, and prefixed runtime trace IDs are produced through `backend/request_identity.py`.
14. RequestMetadata workspace/agent mapping uses `backend/request_metadata.py`.
15. Runtime UUIDs and prefixed runtime IDs use `backend/runtime_ids.py`.
16. Mapping copies and metadata/payload merges use `backend/mapping_utils.py`.
17. Cache, source-freshness, policy, and execution-envelope reason strings use `backend/reason_messages.py`.
18. Sub-agent status vocabulary, priority, and aggregation use `backend/subagent_status.py`.
19. Sub-agent output construction and model coercion use `backend/subagent_output_contracts.py`.
20. Mock sub-agent names, artifact types, output text, error text, synthesis text, and orchestration telemetry use `backend/mock_agent_contracts.py`.
21. Generated-image review status vocabulary and checks use `backend/review_status.py`.
22. Critic/Curator rubric categories and decisions use `backend/critic_rubric.py`.
23. Text tokenization, label/tag normalization, and contextual snippets use `backend/text_utils.py`.
24. Numeric clamps, rounded averages, and vector similarity use `backend/numeric_utils.py` directly at scoring boundaries.
25. Connection names, target setting fields, defaults, secret aliases, endpoint URL composition, env-example rendering, and runtime env resolution use `backend/connection_settings.py`.
26. Cache, provenance, execution-envelope, source freshness, observability, and persistence timestamps use `backend/time_utils.py` directly for UTC creation and normalization.
27. Connector payload string-field extraction, tolerant string reads, and nested object extraction use `backend/payload_fields.py`.
28. Provider response object/dict field access, first-choice message content extraction, and shape validation use `backend/response_fields.py`.
29. Connector URL/domain and relative API path validation uses `backend/url_utils.py`.
30. Connector HTTP method vocabulary and normalization uses `backend/http_methods.py`.
31. Operation constants, classification term maps, and sensitivity rules use `backend/operations.py`.
32. Classifier confidence and reason formatting use `backend/classification_contracts.py`.
33. Request kind, channel, operation, and audit event type contracts use `backend/interface_types.py`.
34. Telemetry stages and log levels use `backend/observability.py`.
35. Publishing outcome statuses use `backend/publishing_status.py`.
36. Pydantic model/dict coercion at service, adapter, and domain boundaries calls `backend/model_coercion.py` directly.
37. Knowledge Agent names, retrieval artifact types, approved-source payload flags, collection defaults, policy notes, and summary vocabulary use `backend/knowledge_contracts.py`.
38. Observability fields and metric tags use `backend/audit.py` redacted mapping helpers for telemetry-safe dict payloads.
39. ComfyUI generated-image URI conventions, response image validation messages, and response image storage references use `backend/comfyui_contracts.py`.
40. Source registry missing-row messages use `backend/source_registry_contracts.py`.
41. Execution-envelope validation failure and required-envelope messages use `backend/execution_gate_messages.py`.
42. Secret-like value detection, assignment scanning, and redaction use `backend/secret_redaction.py`.
43. Reviewable text-file suffixes and recursive scanner discovery use `backend/file_scanning.py`.
44. Markdown heading extraction for documentation validators uses `backend/markdown_utils.py`.
45. Optional source registry row lookup uses `SourceFreshnessRegistry.find_source`.
46. Publishing side-effect audit operation values use `backend/operations.py`.
47. Gated adapter operation values use `backend/operations.py` directly.
48. Slack source labels and adapter validation messages use `backend/slack_contracts.py`.
49. GitHub adapter action labels, validation messages, and token-purpose text use `backend/github_contracts.py`.
50. Source ingestion approved-domain defaults and rejection messages use `backend/source_ingestion_contracts.py`.
51. Production readiness service URLs, `.env.example` rendering, and health/backup/restore endpoint commands use `backend/connection_settings.py`.
52. Production readiness Docker Compose, curl, and MinIO command strings use `backend/shell_commands.py`.
53. Production readiness backup directories, container dump paths, and MinIO aliases use `backend/readiness_paths.py`.
54. Repository artifact paths, backend module discovery, and source-text reads for Compose, env, runbook, OPA policy, PostgreSQL schema, and backend module files use `backend/repo_paths.py`.
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
  connection settings helper before adapters read provider credentials.
- `.env.example` must match the shared connection settings registry rendering.
- Readiness health, backup, and restore endpoint commands compose service URLs
  through the shared connection settings helper.
- Readiness Docker Compose, curl, and MinIO command syntax is built through the
  shared shell command helper.
- Readiness backup directories, container dump paths, and MinIO aliases use the
  shared readiness path contract.
- Repository artifact paths, backend module discovery, and source-text reads use
  the shared repo path contract before runtime review checks, scaffold
  validators, or contract guards read checked-in files.
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
   - Request metadata workspace/agent fields use the shared metadata mapping helper.
   - Canonical JSON, SHA-256 digest creation, HMAC signing, and security-review serialization flow through the shared hash helper.
   - Channel adapters and tool hooks use the shared request identity helper for text normalization, stable event ids, and prefixed trace ids.
   - Slack adapter payload parsing, request identity, and secret redaction call the shared helpers directly at the adapter boundary.
   - Slack source labels and adapter validation messages use the shared Slack contract before adapter errors are raised.
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

5. Reuse Decision
   - Read-only repeat requests check approved cache and source freshness.
   - Cache, source-freshness, policy, and execution-envelope decision text uses the shared reason-message helper.
   - Cache replay request-kind and operation checks use shared interface and operation constants.
   - Source ingestion validates absolute HTTP(S) source domains through the shared URL helper.
   - Source ingestion approved-domain defaults and rejection messages use the shared source-ingestion contract.
   - Source snapshot content hashes and version tags use the shared canonical hash helper.
   - Source ingestion calls shared hash/version helpers directly before registry and snapshot writes.
   - Source registry lookup failures format missing-row messages through the shared source registry contract helper.
   - Source ingestion checks for existing registry rows through the source registry optional lookup API.

6. Orchestrate
   - Fresh or changed requests route through OpenClaw sub-agents.
   - Sub-agent outputs are constructed through the shared output contract helper.
   - Mock orchestration agent names and artifact types use the shared mock-agent contract.
   - Retrieval embeddings, snippets, and rubric labels use shared text tokenization and label normalization.
   - Knowledge retrieval result snippets use the shared contextual snippet helper.
   - Retrieval vector similarity, rubric scoring, and orchestration confidence use shared numeric helpers.
   - Critic/Curator score bounds call the shared numeric clamp directly without local wrapper functions.

7. Validate
   - Runtime validates `SubAgentOutput`, compares results, retries if needed,
     and synthesizes one response.
   - Knowledge and mock sub-agent output coercion uses the shared sub-agent output constructor.
   - Domain and adapter inputs and structured outputs coerce model-or-dict payloads through the shared model coercion helper.
   - Provider SDK object-or-dict responses are read through the shared response-field helper.
   - Connector HTTP methods are normalized through the shared HTTP method helper.
   - GitHub adapter labels, API validation messages, and token-purpose text use the shared GitHub contract before adapter errors are raised.

8. Execution Gate
   - Any external write, publish, GitHub write, deletion, or image generation
     receives a signed execution envelope.
   - Gated adapters pass shared operation constants directly into the execution gate.
   - Envelope validation failure messages use the shared execution-gate message contract.
   - Execution-envelope signatures use the shared canonical HMAC helper.
   - Envelope issue times, cache checks, source timestamps, telemetry timestamps, and expiry comparisons use direct shared UTC creation and normalization.
   - Connector API paths are normalized and rejected for absolute URLs, traversal,
     backslashes, and control characters before token reads.

9. Deliver
   - Output Tool Agent sends the response or executes the approved action.

10. Audit
   - Every request, cache reuse, policy decision, execution envelope, tool call,
     and artifact is recorded.
   - Security review and scanner paths detect secret-like values through the shared secret-redaction boundary.
   - Security review and scanner paths discover reviewable workspace files through the shared file-scanning boundary.
   - Publishing side-effect audit events use the shared publish operation constant.
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
