# AI-Artist Final Stack Specs - Latest

## Status

```text
Date: 2026-06-01
Implementation status: all 28 tracker tasks complete
Final validation: 553 passed, 1 warning
Live LLM API smoke test: passed with deepseek-open-art
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
backend/api_contracts.py: shared FastAPI app metadata and Safety Service route paths.
backend/app.py: FastAPI endpoints using shared API contracts.
backend/service.py: canonicalization, classification, local policy gate, execution envelope creation using shared signing and service-observability contracts.
backend/policy_contracts.py: shared local default-deny policy version, execution-envelope signing key, signature prefix, runtime-field-backed signature payload, signing/verification helpers, and execution-envelope TTL contracts for policy responses and execution envelopes.
backend/schemas.py: API and SubAgentOutput schemas.
backend/health_contracts.py: shared Safety Service health status, service name, response payload, and readiness signal.
backend/classification_contracts.py: shared classifier confidence and reason formatting.
backend/interface_types.py: shared request kind, channel, operation, and audit event type contracts for schemas and runtime modules.
backend/canonical_hash.py: canonical JSON, SHA-256 digests, canonical HMAC signatures, deterministic ID helpers, version tags, security-review serialization, direct image-provenance text hashes, deterministic test serialization, and deterministic test text hashes.
backend/request_identity.py: request text normalization, direct Safety Service canonicalization/classification normalization, fingerprints, stable request UUIDs, and prefixed runtime trace IDs.
backend/request_metadata_contracts.py: shared request metadata defaults, default request channel, request envelope field names, and fingerprint field names.
backend/request_metadata.py: shared RequestMetadata workspace/agent mapping, canonical request fingerprint field shape, and canonicalization observability field shape using request metadata contracts.
backend/service_observability_contracts.py: shared Safety Service request and policy observability event, message, tag, and field shapes.
backend/runtime_field_contracts.py: shared task-id, execution-envelope-id, client-response, operation, target, request-id, correlation-id, status, request-kind, scope, allow, approval, reason, and policy-version field names for runtime telemetry, policy contexts, OpenClaw metadata, execution-envelope signatures, adapter results, audit response request/correlation/policy-scope fields, mock orchestration task/requester/policy/status fields, Slack local request scope/request-id/result fields, and side-effect audit payloads.
backend/request_scope_contracts.py: shared default requester, policy, publishing actor, and publishing policy scope contracts for schemas, mock orchestration, and publishing audit context.
backend/runtime_ids.py: shared runtime UUID and prefixed runtime ID generation.
backend/mapping_utils.py: shared mapping copy and merge helpers for metadata and payload boundaries.
backend/reason_messages.py: shared cache, source-freshness, policy, and execution-envelope reason strings.
backend/subagent_status.py: shared SubAgentOutput status vocabulary, priority, and counting helpers.
backend/subagent_output_contracts.py: shared SubAgentOutput construction, runtime-field-backed task-id/status payload fields, sub-agent output payload field names, and model-coercion boundary.
backend/review_status.py: shared generated-image review status vocabulary and checks.
backend/critic_rubric.py: shared Critic/Curator rubric categories, pass/fail decision vocabulary, score bounds, pass thresholds, scoring weights, publication penalties, and rubric score helpers.
backend/text_utils.py: shared text tokenization, direct Safety Service classifier token parsing, label normalization, and contextual snippets.
backend/markdown_utils.py: shared Markdown heading extraction for documentation validators.
backend/numeric_utils.py: shared numeric clamps, averages, vector similarity, positive-integer checks, zero-magnitude checks, and numeric/vector validation messages.
backend/time_utils.py: shared UTC datetime creation and normalization for runtime code and tests.
backend/payload_fields.py: shared connector payload string-field and nested-object extraction plus payload validation messages.
backend/response_fields.py: shared provider response field names/access, first-choice message parsing, shape validation, and response validation messages.
backend/url_utils.py: shared URL domain and relative API path validation plus URL validation messages.
backend/http_methods.py: shared HTTP method vocabulary, normalization, and validation messages for connector boundaries.
backend/file_scanning.py: shared reviewable text-file suffixes and recursive scanner file discovery.
backend/operations.py: shared operation constants, classifier terms, and sensitivity rules.
backend/model_coercion.py: shared Pydantic model/dict coercion and validation messages for adapter and domain boundaries.
backend/adapter_gate_contracts.py: shared gated-adapter action and target labels for execution-envelope messages.
backend/adapter_results.py: shared gated adapter result field vocabulary and field mapping with generic execution-envelope/client-response/request/operation/target fields reused from runtime field contracts.
backend/audit_contracts.py: shared audit scope payload field names, runtime policy-scope/request/correlation-id fields, accepted response flag, and audit response payload shape.
backend/side_effect_audit_contracts.py: shared side-effect audit payload field names that reuse generic audit scope and runtime field contracts.
backend/side_effect_audit.py: shared side-effect audit payload and event recording using shared payload field, runtime field, and audit event type contracts.
backend/secret_redaction.py: shared secret-key detection, token-shape detection, assignment-pattern detection, structured unredacted-secret checks, and redaction utilities.
backend/comfyui_contracts.py: shared ComfyUI generated-image URI convention, response image field names, response image validation messages, and response-image storage reference helper.
backend/source_registry_contracts.py: shared source registry missing-row message, dependency-role, empty change-sequence, and initial change-sequence contracts.
backend/source_freshness_contracts.py: shared source-freshness schema defaults, unchanged-source predicate, and unchanged-source-freshness payload helper for fresh source snapshots, cache replay, security review probes, and gated-adapter test envelopes.
backend/source_ingestion_contracts.py: shared source ingestion approved-domain defaults, rejection message, registry metadata key contracts, and registry metadata payload shape.
backend/slack_contracts.py: shared Slack source label, event field names, scope, runtime requester/policy/request-id fields for local-request payloads, outbound payload, runtime client-response field for post-result payloads, validation message contracts, and token-purpose text.
backend/github_contracts.py: shared GitHub adapter action labels, validation messages, token-purpose text, and token-required message routing through connection settings.
backend/audit.py: in-memory audit repository, recursive secret redaction, redacted mapping helper for telemetry/audit payloads, and audit response construction through shared audit contracts.
backend/execution_gate_messages.py: shared execution-envelope validation failure, signature, and required-envelope message contracts.
backend/execution_gate.py: shared execution-envelope coercion, semantic validation, expiry validation, and signature verification for gated adapters.
backend/response_cache_contracts.py: shared response-cache reuse telemetry event, message, metric-tag, and structured-field shapes with generic operation/request-kind/reason field names reused from runtime field contracts.
backend/response_cache.py: approved read-only response cache using shared request kind, operation, reason, time, and cache observability boundaries.
backend/source_freshness.py: dependency snapshot, stale-source checks, source registry role/change-sequence contracts, and key/id source registry lookup.
backend/source_ingestion.py: approved local source ingestion with direct canonical hash/version, URL-domain validation, registry metadata payload, and source-registry default boundaries.
backend/connection_settings.py: registry-driven env var names, defaults, aliases, runtime env resolution, runtime secret resolution with registered env-var-to-setting-name derivation, connection error messages, and guards, endpoint URL composition, env-example rendering/parsing, env-example validation helpers, connection settings loader, and the project-standard deepseek-open-art LLM API key.
backend/adapter_secrets.py: shared adapter secret lookup that delegates standard env-var setting-name derivation to the connection registry, supports custom env names and explicit injected secrets, and wraps adapter-specific configuration errors.
backend/shell_commands.py: shared shell command and process argument construction for Docker Compose, curl, MinIO, and OPA command definitions plus subprocess execution defaults and delimited process-output parsing.
backend/readiness_paths.py: shared production readiness backup paths, container dump path, and MinIO source alias.
backend/repo_paths.py: shared repository artifact paths, repo-root resolution, workspace paths/text reads, backend module discovery, source-text readers, and source-inspection file reads for Compose, env, runbook, OPA policy, PostgreSQL schema, and backend module files.
tests/path_helpers.py: shared test project root, checked-in project text reads, backend source reads, test source reads, and repo-wide test-module source iteration for guard tests.
tests/cache_entry_helpers.py: shared approved response-cache entry construction for cache, source-freshness, and observability tests, including cache identity, request fingerprint, requester/policy scope, read-only operation, response body, reuse flags, source state, and cache timestamp defaults.
tests/connection_env_helpers.py: shared test env builders and secret constants for LLM, Slack, GitHub, and full connection-settings test scenarios.
tests/execution_envelope_helpers.py: shared execution-envelope construction for gated-adapter and policy-path tests, including approved, unapproved, unchanged-source, and stale-source fixtures.
tests/gated_adapter_helpers.py: shared adapter-specific request, envelope, adapter/client harness, Publishing Agent request/harness, and fake-client defaults for ComfyUI, GitHub, Publishing adapter tests, and Publishing Agent tests, including stable request IDs, targets, operation defaults, payload defaults, request construction, approved/unapproved envelope construction, mocked client responses, ComfyUI and Publishing adapter setup, Publishing Agent local/secret-echo setup, GitHub token/env adapter setup, and secret-echo client responses.
tests/human_approval_helpers.py: shared HumanApproval construction for execution-envelope, execution-gate, policy-contract, adapter-result, and publishing-adapter tests, including approved/unapproved state, approver scope, and approval timestamp defaults.
tests/image_provenance_helpers.py: shared image provenance store, payload, and record construction for image provenance, Critic/Curator, and security-review tests, including stable prompt, workflow, model, seed, source references, storage URI, review status, timestamp, and record defaults.
tests/knowledge_agent_helpers.py: shared Knowledge Agent harness, in-memory vector store, deterministic embedding model, source-document, approved sample source, and vector-point setup for Knowledge Agent tests.
tests/llm_api_smoke_helpers.py: shared OpenAI-compatible recording LLM client, recording chat completions, response id, and response content for provider-neutral LLM API smoke tests.
tests/openclaw_hook_helpers.py: shared OpenClaw safety-hook recording Safety Service client, recording adapter, mock orchestration adapter, and event labels for OpenClaw-to-safety and observability integration tests.
tests/policy_request_helpers.py: shared policy-evaluate request construction for cache, freshness, observability, and Safety Service policy-path tests.
tests/policy_response_helpers.py: shared approved policy-evaluate response construction for cache and source-freshness tests, including allow, reason, human-approval, and policy-version defaults.
tests/request_metadata_helpers.py: shared RequestMetadata construction for request metadata, Safety Service unit, and observability tests, including workspace and agent defaults.
tests/safety_service_client_helpers.py: shared FastAPI Safety Service TestClient and request helpers for endpoint, audit, OpenClaw hook, and observability tests.
tests/service_request_helpers.py: shared Safety Service canonicalize and classify request construction for unit, observability, and request-metadata tests, including standard request text, normalized text, observability request text, default-scope request construction, requester scope, policy scope, channel, metadata, and explicit operation defaults.
tests/secret_test_helpers.py: shared secret-bearing test payloads, secret constants, and redaction assertions for audit, security review, secret-redaction, and side-effect audit tests.
tests/slack_adapter_helpers.py: shared Slack adapter test harness, deterministic Slack client, inbound event payload, channel/user/team/event IDs, timestamps, and normalized text defaults.
tests/source_registry_helpers.py: shared SourceFreshnessRegistry and source-ingestion harness construction for source freshness and source ingestion tests, including empty, single-source, two-source, style-source, approved-domain, snapshot-repository, service, and sample-candidate setup.
tests/subagent_output_helpers.py: shared raw SubAgentOutput payload construction for schema-boundary tests using the shared sub-agent output field contracts.
tests/tool_call_helpers.py: shared ToolCallRequest construction for OpenClaw safety hook and observability tests, including default operation, request kind, scope, correlation ID, request ID, metadata, arguments, and source freshness setup.
backend/llm_api_contracts.py: shared provider-neutral LLM chat request field names, role vocabulary, smoke request body construction, redacted request-log payload shape, and smoke result payload shape.
backend/llm_api_smoke.py: provider-neutral LLM API configuration, named smoke-test connection purpose, centralized smoke request defaults/overrides, centralized smoke timeout, shared runtime secret resolution, and redacted smoke request path using shared LLM request/result contracts.
backend/openclaw_contracts.py: shared OpenClaw tool policy metadata, redaction, metric tag, and structured telemetry field shapes.
backend/openclaw_hook.py: pre-tool Safety Service hook using direct shared request-kind and secret-redaction boundaries.
backend/mock_agent_contracts.py: shared mock sub-agent names, artifact types, output text, error text, simulation metadata lookup, synthesis text, orchestration telemetry event/message/metric contracts, and orchestration telemetry field/tag shapes with generic task/requester/policy/status fields reused from runtime field contracts.
backend/knowledge_contracts.py: shared Knowledge Agent name, retrieval artifact, vector payload fields/shape, vector payload read helpers, approved payload flag, collection default, embedding defaults, stable token-index hashing, vector-search limit/sort behavior, result score cutoff/precision, policy note, and summary vocabulary.
backend/orchestrator.py: mock sub-agent routing and synthesis using shared mock-agent contracts.
backend/knowledge.py: deterministic source-cited retrieval using shared Knowledge Agent contracts for output, vector payload writes/reads, embedding, vector-search, and result-score boundaries.
backend/comfyui_adapter.py: execution-envelope-gated image generation adapter using direct shared operation constants.
backend/image_provenance.py: prompt/workflow hashing and provenance records using shared ComfyUI image response/storage contracts and direct model-coercion boundary.
backend/critic_curator.py: deterministic image critique rubric using direct model-coercion and shared rubric scoring boundaries.
backend/slack_adapter.py: mocked Slack request/response adapter using shared payload, request identity, secret-redaction, and adapter-secret boundaries directly.
backend/publishing_contracts.py: shared local publishing ID prefix, dry-run response fields, deterministic ID material shape, and publishing response status/target fields that reuse runtime field contracts.
backend/publishing.py and backend/publishing_adapter.py: approval-gated publishing path using direct shared operation, publishing scope, and publishing response-shape constants.
backend/publishing_status.py: shared publishing outcome status vocabulary and checks.
backend/github_adapter.py: GitHub write adapter with token isolated to adapter boundary, explicit-token and env-token resolution routed through the shared adapter secret helper, and direct shared operation and URL path validation.
backend/observability.py: telemetry stage/log-level constants, default metric values, metric-name constants/formatting, trace-id fallback formatting, event-message formatting, traces, metrics, and structured logs using shared audit redacted-mapping boundary.
backend/security_review_contracts.py: shared security review finding surfaces, messages, probe event/trace, default-deny pattern, target formatting, and prompt-hash field contracts.
backend/security_review.py: deterministic security checklist helpers using shared security-review contracts.
backend/readiness.py: production readiness schema, centralized readiness detail messages, and runbook validators.
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
valid operation-matching execution envelope with a verified shared HMAC
signature exists.
External publish/write paths require human approval.
OpenClaw agents, prompts, logs, audit payloads, and memory files must not
contain raw API keys, OAuth tokens, Slack tokens, GitHub tokens, signing keys, or
private webhook secrets.
Safety Service health status, service name, response payload, and readiness
expected-signal text must flow through backend/health_contracts.py before
endpoint, schema, or runbook readiness health-check logic is changed.
Safety Service API metadata and route paths must flow through
backend/api_contracts.py before FastAPI decorators, endpoint tests, or
interface docs change.
Connection names, defaults, secret aliases, target setting fields, registered env-var-to-setting lookup, endpoint URL
composition, env-example rendering/parsing/validation, runtime env resolution, runtime secret resolution, connection error messages, and env-access guards must be changed through
backend/connection_settings.py before adapter-specific code; the standard LLM
API secret key is `deepseek-open-art`, with `DEEPSEEK_API_KEY` retained only as
a legacy loader alias and excluded from rendered project setup examples.
Runtime secret lookup for registered env vars must derive target connection
settings inside backend/connection_settings.py before LLM, Slack, GitHub, or
future adapters read runtime secrets.
Adapter secret lookup must delegate standard setting-name derivation to
backend/connection_settings.py before Slack, GitHub, or future adapters read
runtime tokens.
LLM smoke-test prompts, reasoning effort, thinking mode, timeout, request payload
construction, runtime secret lookup, and redacted request recording must flow
through backend/llm_api_smoke.py before live-provider diagnostics are changed.
Shell command strings and process argument lists for Docker Compose, curl,
MinIO, and OPA commands, subprocess execution defaults, and delimited process-output parsing must flow
through backend/shell_commands.py before production readiness command
definitions, test process invocations, or migration output parsers are changed.
Production readiness backup directories, container dump paths, and MinIO source
aliases must flow through backend/readiness_paths.py before runbook or command
definitions are changed.
Production readiness env, runbook, and command validation detail messages must
flow through backend/readiness.py helpers before readiness checks expose new
human-readable status text.
Repository artifact paths, repo-root resolution, workspace paths/text reads,
backend module discovery, source-text reads, and source-inspection file reads
must flow through backend/repo_paths.py before runtime review checks, scaffold
tests, contract guards, or documentation validators reference Compose, env,
runbook, OPA policy, PostgreSQL schema, workspace, or backend module files.
Repo-wide validation tests that scan checked-in project, backend, or test source
must use tests/path_helpers.py for project root resolution, project text reads,
backend source reads, test source reads, and source iteration.
Safety Service endpoint, audit, OpenClaw hook, and observability tests that need
the FastAPI test client must use tests/safety_service_client_helpers.py before
constructing TestClient directly.
Cache, source-freshness, and observability tests that need approved cache
entries must use tests/cache_entry_helpers.py before constructing
ApprovedResponseCacheEntry directly.
Response-cache tests must call tests/cache_entry_helpers.py directly for
standard approved cache entries before adding local base-cache-entry wrappers.
Connection tests that need LLM, Slack, GitHub, or full connection env fixtures
must use tests/connection_env_helpers.py before repeating env-var names,
provider keys, or adapter token literals.
LLM API smoke tests that need mocked OpenAI-compatible provider clients must
use tests/llm_api_smoke_helpers.py before defining local recording client
classes.
Redaction and security-review tests that need secret-bearing payloads,
workspace secret lines, observability fields, or side-effect client responses
must use tests/secret_test_helpers.py before repeating token-shaped literals.
Slack adapter tests that need adapter/client setup, deterministic Slack clients,
inbound event payloads, event identity values, timestamps, or normalized text
must use tests/slack_adapter_helpers.py before constructing SlackAdapter
directly or defining local Slack client or event payload helpers.
Source freshness and source ingestion tests that need local source registries,
source-ingestion services, snapshot repositories, or sample candidates must use
tests/source_registry_helpers.py before constructing SourceFreshnessRegistry,
SourceIngestionService, InMemorySourceSnapshotRepository, or
SourceIngestionCandidate fixtures directly.
Source freshness tests must call tests/policy_request_helpers.py and
tests/cache_entry_helpers.py directly before adding local policy-request or
cache-entry wrappers.
SubAgentOutput schema-boundary tests that need raw valid payload dictionaries
must use tests/subagent_output_helpers.py before defining local payload builders.
Knowledge Agent tests that need agents, in-memory vector stores, embedding
models, source documents, approved sample sources, or vector points must use
tests/knowledge_agent_helpers.py before constructing KnowledgeAgent,
InMemoryQdrantVectorStore, KnowledgeSourceDocument, or VectorPoint fixtures
directly.
OpenClaw hook and observability tests that need standard tool-call requests
must use tests/tool_call_helpers.py before constructing ToolCallRequest
directly.
OpenClaw hook and observability tests that need recording safety clients,
recording adapters, mock orchestration adapters, or event labels must use
tests/openclaw_hook_helpers.py before defining local recording adapter classes.
Policy-path tests that need cache-reuse or Safety Service policy requests must
use tests/policy_request_helpers.py before cache, source freshness,
observability, policy-contract, Safety Service unit, or future policy-path
tests construct PolicyEvaluateRequest directly.
Response-cache tests must call tests/policy_request_helpers.py directly for
standard policy requests before adding local base-policy-request wrappers.
Cache and source-freshness tests that need approved policy responses must use
tests/policy_response_helpers.py before constructing PolicyEvaluateResponse
fixtures directly.
Request metadata, Safety Service unit, and observability tests that need
workspace/agent metadata must use tests/request_metadata_helpers.py before
constructing RequestMetadata fixtures directly.
Safety Service unit, observability, request-metadata, and future service-boundary tests that need canonicalize or classify request models must
use tests/service_request_helpers.py before constructing CanonicalizeRequest or
ClassifyRequest directly.
Execution-envelope, execution-gate, policy-contract, adapter-result, and
publishing-adapter tests that need human approval state must use
tests/human_approval_helpers.py before constructing HumanApproval fixtures
directly.
Image provenance, Critic/Curator, security-review, and future artifact
provenance tests that need provenance stores, payloads, or records must use
tests/image_provenance_helpers.py before constructing LocalImageProvenanceStore
or ImageProvenanceRecord directly or duplicating standard provenance payloads.
Publishing Agent tests that need local publisher clients, secret-echo publisher
clients, publish requests, targets, payloads, or approved/unapproved publishing
envelopes must use tests/gated_adapter_helpers.py before constructing
PublishingAgent, LocalPublishingClient, PublishingAgentRequest, or
Publishing-specific envelope builders directly.
Gated-adapter and policy-path tests that need approved, unapproved, unchanged-source, or stale-source execution envelopes must
use tests/execution_envelope_helpers.py before Safety Service unit,
policy-contract, publishing-agent, or future policy-path test modules construct
envelope requests directly. ComfyUI, Publishing, GitHub, and future gated
adapter tests that need adapter-specific request IDs, targets, operation
defaults, payload defaults, request construction, approved/unapproved
envelopes, or adapter/client harness setup must use
tests/gated_adapter_helpers.py before constructing adapters directly or
defining adapter-local request or envelope wrappers.
Gated adapter and publishing-agent tests that need deterministic fake ComfyUI,
GitHub, publishing, or secret-echo publishing clients must use
tests/gated_adapter_helpers.py before defining local fake client classes.
Execution-envelope validation, expiry checks, and signature verification must
flow through backend/execution_gate.py before adapter-specific side-effect logic.
Execution-envelope validation failure, signature failure, and required-envelope
messages must flow through backend/execution_gate_messages.py before gated
adapters expose envelope errors.
Secret detection patterns, assignment scanning, structured unredacted-secret checks, and replacement behavior must
flow through backend/secret_redaction.py before adapter-specific logging,
response shaping, security review, or future scanner logic.
OpenClaw tool policy metadata, metadata redaction, tool metric tags, preflight
fields, decision fields, and executed fields must flow through
backend/openclaw_contracts.py before the hook prepares Safety Service policy
requests or tool telemetry.
Slack payload parsing, request text normalization, stable request IDs, and
response redaction must call the shared payload, request identity, and
secret-redaction helpers directly at the adapter boundary.
Slack source labels, event field names, scope formatting, runtime-field-backed local-request scope/request-id payloads,
outbound payloads, post-result payloads, and adapter validation messages must flow through
backend/slack_contracts.py before Slack event parsing or response formatting
raises adapter errors.
Gated adapter action and target labels must flow through
backend/adapter_gate_contracts.py before execution-envelope message construction.
Gated adapter result envelope IDs, request IDs, operation, target, client
response field vocabulary, and result field mapping must flow through
backend/adapter_results.py and backend/runtime_field_contracts.py before
adapter-specific return dataclasses or side-effect audit payloads add result
fields.
Audit scope payload field names, audit policy-scope/request-id/correlation-id field names,
and audit response payload shapes must flow through backend/audit_contracts.py
and backend/runtime_field_contracts.py before audit records, audit responses,
or side-effect audit payloads extract actor/policy scopes or change
accepted-event shape.
Side-effect audit payload field names and event types must flow through
backend/audit_contracts.py, backend/runtime_field_contracts.py,
backend/adapter_results.py, backend/side_effect_audit_contracts.py,
backend/side_effect_audit.py, and backend/interface_types.py before
adapter-specific agents persist tool-call audit events.
Canonical JSON, SHA-256 digests, canonical HMAC signatures, deterministic local IDs, version tags, security-review serialization, direct image-provenance text hashes, deterministic test serialization, and deterministic test text hashes must
flow through backend/canonical_hash.py before request fingerprints, artifact
hashes, image provenance hashes, source snapshot versions, signatures, mocked external IDs, security-review scans, deterministic test serializations, or deterministic test text hashes are created.
Request text normalization, fingerprint wrappers, stable channel request UUIDs,
and prefixed runtime trace IDs must flow through backend/request_identity.py
before service or adapter specific request identity logic is added.
Safety Service canonicalization and classification must call
backend/request_identity.py directly for request text normalization.
Request metadata defaults, default request channel, request envelope field names,
RequestMetadata workspace/agent mapping, canonical request fingerprint field
shape, and canonicalization observability field shape must flow through
backend/request_metadata_contracts.py and backend/request_metadata.py before
service fingerprinting, schema defaults, observability metric tags, or
structured observability fields are built.
Safety Service canonicalization, classification, and policy observability event,
message, tag, and field shapes must flow through
backend/service_observability_contracts.py before service telemetry is emitted.
Execution-envelope-id, operation, target, request-id, correlation-id, status, request-kind, requester/policy scope, allow,
human-approval, reason, and policy-version field names must flow through
backend/runtime_field_contracts.py before service observability, OpenClaw tool
telemetry, execution-envelope signature payloads, adapter results, audit
responses, Slack local request/result payloads, publishing response contracts,
side-effect audit payloads, or future policy context field shapes are
changed.
Default requester, policy, publishing actor, and publishing policy scopes must
flow through backend/request_scope_contracts.py before schemas, mock
orchestration, publishing audit context, or future request envelopes change
local scope defaults.
Runtime UUIDs and prefixed runtime IDs must flow through
backend/runtime_ids.py before service, schema, adapter, orchestration,
freshness, retrieval, or review-specific runtime IDs are created.
Mapping copies and metadata/payload merges must flow through
backend/mapping_utils.py before domain-specific copy or merge logic is added.
Cache, source-freshness, policy, and execution-envelope reason strings must
flow through backend/reason_messages.py before service or cache decision text is
added.
Policy response and execution-envelope policy versions, local execution-envelope
signing key, signature prefix, runtime-field-backed signature
payload/signing/verification helpers, and execution-envelope TTL must flow
through backend/policy_contracts.py and backend/runtime_field_contracts.py
before local default-deny or envelope-signing contracts change.
Source registry missing-row messages must flow through
backend/source_registry_contracts.py before source freshness or future
persistence adapters raise missing-row errors.
Source dependency roles plus empty and initial source change sequence defaults must flow
through backend/source_registry_contracts.py before freshness snapshots or
registry writes change source semantics.
SourceFreshness schema defaults, unchanged-source checks, and unchanged-source
payload construction must flow through backend/source_freshness_contracts.py
before default freshness, cache replay semantics, security review probes, or
gated-adapter test envelope freshness setup change.
Existing source registry row checks must call SourceFreshnessRegistry.find_source
or SourceFreshnessRegistry.find_source_by_id before ingestion, stale-source
checks, or future persistence code handles optional source rows.
SubAgentOutput status vocabulary, priority, and aggregation must flow through
backend/subagent_status.py before schema or orchestration-specific status
logic is added.
SubAgentOutput construction, task-id/status field spellings, sub-agent output
payload field names, and model coercion must flow through backend/subagent_output_contracts.py and
backend/runtime_field_contracts.py before Knowledge retrieval, mock
orchestration, or future sub-agent adapters return structured agent outputs.
Mock sub-agent names, artifact types, output text, error text, synthesis text,
orchestration telemetry events/messages/metrics, and orchestration telemetry
field/tag shapes must flow through backend/mock_agent_contracts.py before
orchestration-specific agent fixtures or telemetry are changed, with generic
task/requester/policy/status fields reused from backend/runtime_field_contracts.py.
Knowledge Agent names, retrieval artifact metadata, vector payload fields/shape,
vector payload write/read helpers, approved-source payload flags, collection defaults, embedding defaults, stable
token-index hashing, vector-search limit/sort behavior, result score
cutoff/precision, policy notes, and summary vocabulary must flow through
backend/knowledge_contracts.py before retrieval-specific behavior is changed.
Generated image review status vocabulary and checks must flow through
backend/review_status.py before provenance, critic, or publishing-specific
review status logic is added.
Critic/Curator rubric categories, decisions, score bounds, pass thresholds,
category weights, publication penalties, score conversion helpers, and pass/fail
checks must flow through backend/critic_rubric.py before scorer-specific rubric
logic is added.
Text tokenization, label/tag normalization, and contextual snippets must flow through
backend/text_utils.py before classifier, retrieval, or rubric-specific token
parsing logic is added.
Safety Service classification must call backend/text_utils.py directly for
classifier token parsing.
Markdown heading extraction must flow through backend/markdown_utils.py before
readiness or future documentation validators inspect section headings.
Numeric clamps, rounded averages, vector similarity, positive-integer checks,
zero-magnitude checks, and numeric/vector validation messages must flow through
backend/numeric_utils.py before orchestration, retrieval, or rubric-specific
scoring logic is added.
Critic/Curator rubric score bounds must call backend/critic_rubric.py shared
rubric score helpers before category or publication-readiness scores are emitted.
UTC datetime creation and normalization must flow directly through backend/time_utils.py
before cache, provenance, execution gate, source freshness, observability, or
future persistence time comparisons are added.
Tests that need current UTC time must call backend/time_utils.py instead of
calling datetime.now(timezone.utc) directly.
Connector payload required/optional string extraction, tolerant string reads,
nested-object extraction, and payload validation messages must flow through
backend/payload_fields.py before adapter-specific payload parsing logic is added.
Provider response object/dict field access, shape validation, and response validation
messages must flow through backend/response_fields.py before adapter-specific SDK
response parsing logic is added.
Source ingestion approved-domain defaults, rejection text, registry metadata
keys, and registry metadata payload shape must flow through
backend/source_ingestion_contracts.py before ingestion allowlists, rejection
messages, or registry metadata writes are changed.
URL/domain extraction, relative API path validation, and URL validation messages
must flow through backend/url_utils.py before connector-specific URL allowlist or
path-safety logic is added.
HTTP method vocabulary, normalization, and validation messages must flow through
backend/http_methods.py before connector-specific method allowlists are added.
GitHub adapter action labels, target labels, API validation messages, token
purpose text, token-required message routing, and explicit/env token lookup
must flow through backend/github_contracts.py, backend/connection_settings.py,
and backend/adapter_secrets.py before GitHub adapter errors are raised.
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
execution-envelope validation. Gated adapter action and target labels must call
backend/adapter_gate_contracts.py directly.
Request kind, channel, operation, and audit event type contracts must flow
through backend/interface_types.py before schema, classifier, or audit-specific
literal types are added.
Telemetry stages, log levels, default metric values, metric-name constants/formatting,
trace-id fallback formatting, and event-message formatting must flow through
backend/observability.py constants before service, cache, orchestration, tool,
or review-specific telemetry calls are added.
Security review finding surfaces, messages, probe event/trace IDs, policy
default-deny pattern, review targets, and prompt-hash field names must flow
through backend/security_review_contracts.py before checklist logic changes.
Response-cache reuse telemetry event, message, metric-tag, and structured-field
shapes must flow through backend/response_cache_contracts.py before cache reuse
observability changes, with generic operation/request-kind/reason fields reused
from backend/runtime_field_contracts.py.
Publishing outcome status values must flow through backend/publishing_status.py
before publishing agent or side-effect audit status text is added.
Local publishing dry-run response fields, deterministic ID prefix, ID material
shape, and publishing response status/target aliases must flow through
backend/publishing_contracts.py and backend/runtime_field_contracts.py before
local or future external publisher response logic changes.
Pydantic model/dict coercion and validation messages at adapter and domain
boundaries must flow through backend/model_coercion.py before direct model
validation or one-off validation wrappers are added.
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
Latest project review and optimization proposals: validation_reports/project_review_summary_and_optimization_proposals_2026-06-01.md
```
