# AI-Artist Task Validation Matrix

Every implementation task has a concrete validation test. Task status may move
to `Erledigt` only when the validation test passes and the related interface
contract is satisfied.

| ID | Task | Validation Test | Status | Finished |
|---|---|---|---|---|
| T01 | Stack decision: OpenClaw + provider-neutral LLM API | Documentation scan confirms OpenClaw is the control plane, provider-neutral LLM API is the primary LLM, and deprecated architecture terms are absent. | Bestanden | 2026-05-30 |
| T02 | Project documentation and tracker alignment | Manifest includes all new docs, tracker dashboard totals match detail-plan status counts, and validation matrix exists. | Bestanden | 2026-05-30 |
| T03 | Repository scaffold | `pytest`, lint command, and a tree check confirm `backend/`, `workspaces/`, `policies/`, `tests/`, and `docker-compose.yml` exist. | Bestanden | 2026-05-31 |
| T04 | Docker Compose services | `docker compose config` succeeds and service health checks pass for PostgreSQL, Qdrant, MinIO, Redis, and OPA. | Bestanden | 2026-05-31 |
| T05 | FastAPI Safety Service endpoints | API, health-contract, request-metadata, interface-type, request-identity, text-utility, operation-registry, and reason-message tests call `/health`, `/v1/requests/canonicalize`, `/v1/requests/classify`, and `/v1/policy/evaluate` with expected schemas, centralized health response payload, centralized workspace/agent metadata mapping, stable fingerprints, centralized token parsing, centralized operation inference, and centralized policy reason text. | Bestanden | 2026-05-31 |
| T06 | OPA default-deny policies | Policy tests prove write, publish, delete, GitHub write, and cache replay are denied by default and allowed only with valid policy inputs. | Bestanden | 2026-05-31 |
| T07 | PostgreSQL migrations | Migration test applies schema from empty DB, verifies all query/source/cache/audit tables and indexes, then rolls back cleanly. | Bestanden | 2026-05-31 |
| T08 | OpenClaw AI-Artist workspace | Workspace test confirms required `SOUL.md`, `IDENTITY.md`, `USER.md`, `AGENTS.md`, `TOOLS.md`, `MEMORY.md`, and memory folders exist. | Bestanden | 2026-05-31 |
| T09 | Provider-neutral LLM API configuration | Smoke, connection-settings, and response-field tests load DeepSeek model env vars through the shared connection registry/runtime env resolution, call the OpenAI-compatible LLM API with a redacted request, and record response id/model/content through shared dict/SDK response-field and first-choice message parsing without logging secrets. | Bestanden | 2026-05-31 |
| T10 | OpenClaw safety-service tool hook | Integration, request-identity, and secret-redaction tests attempt a tool call, build prefixed tool-call trace IDs through the shared request identity helper, call shared secret redaction directly for Safety Service metadata, and confirm Safety Service receives the pre-execution request before any adapter runs. | Bestanden | 2026-05-31 |
| T11 | `SubAgentOutput` schema | Schema, sub-agent output-constructor, and sub-agent status tests accept valid agent outputs, route output construction/model coercion and status vocabulary through shared modules, and reject missing status, malformed artifacts, invalid confidence, and unstructured errors. | Bestanden | 2026-05-31 |
| T12 | Mock sub-agents | Orchestration, sub-agent output-constructor, mock-agent-contract, sub-agent status, review-status, and numeric-utility tests route one request through all mock agents, collect structured outputs through the shared constructor, and synthesize status/confidence through shared agent/artifact vocabulary, status aggregation, and rounded-average helpers. | Bestanden | 2026-05-31 |
| T13 | Approved read-only response cache | Cache, interface-type, operation, reason-message, and time-utility tests verify only read responses with OPA approval and non-expired UTC-created/cache-normalized entries are replayed through shared request-kind/operation constants, shared reason text, and direct shared UTC helpers. | Bestanden | 2026-05-31 |
| T14 | Source freshness check | Freshness, source-registry-contract, optional source-registry lookup, and time-utility tests increment `source_data_registry.change_seq`, verify UTC source timestamps, prove stale cached responses are blocked, and guard shared missing-row message formatting plus optional source-row lookup. | Bestanden | 2026-05-31 |
| T15 | Audit event log | Audit, observability, secret-redaction, and payload-field tests verify request, policy, reuse, execution-envelope, tool-call, and artifact events are persisted with correlation ids, audit scope strings are extracted through the shared payload helper, and telemetry-safe mappings use the shared audit redaction boundary. | Bestanden | 2026-05-31 |
| T16 | Knowledge Agent retrieval | Retrieval, knowledge-contract, sub-agent output-constructor, text-utility, contextual-snippet, and numeric-utility tests ingest sample source data, tokenize/embed it through shared helpers, query Qdrant with shared vector similarity, return source-cited results through centralized Knowledge Agent output/snippet contracts, and exclude unapproved sources. | Bestanden | 2026-05-31 |
| T17 | ComfyUI adapter behind execution gate | Shared model-coercion, direct operation, execution-gate, execution-gate-message, ComfyUI-contract, and time-utility tests plus adapter tests prove image generation fails without a non-expired valid execution envelope, uses centralized gate failure messages and direct shared UTC expiry checks, follows centralized generated-image URI conventions, and succeeds with a mocked approved envelope. | Bestanden | 2026-05-31 |
| T18 | Image provenance | Artifact, review-status, direct model-coercion, canonical-hash, payload-field, response-field, ComfyUI-contract, and time-utility tests verify prompt hash, workflow hash, model, seed, source refs, storage uri, centralized review status, centralized generated-image URI construction, stable canonical JSON digests, response image shape validation, and direct shared UTC timestamps are stored for every image. | Bestanden | 2026-05-31 |
| T19 | Critic/Curator rubrics | Critic-rubric, review-status, text-utility, numeric-utility, direct numeric-clamp, and direct model-coercion tests score sample images or mocked image metadata with shared rubric category/decision vocabulary, shared label/token normalization, shared review-status checks, and direct shared score clamping/averages, returning structured critique, pass/fail, and improvement notes. | Bestanden | 2026-05-31 |
| T20 | Slack development channel | Slack adapter, request-identity, payload-field, and secret-redaction tests use a mocked Slack API to confirm inbound request normalization, nested event object validation, stable request IDs, direct shared helper usage at the adapter boundary, outbound response formatting, and token redaction. | Bestanden | 2026-05-31 |
| T21 | Source ingestion | Ingestion, canonical-hash, URL utility, and source-registry lookup tests import approved sample sources, store snapshots, record source registry rows, call shared hash/version, URL-domain, and optional registry lookup helpers directly, create stable source version tags, and reject disallowed or non-http source domains. | Bestanden | 2026-05-31 |
| T22 | Publishing Agent with human approval | Shared direct operation, execution-gate, canonical ID, response-field, publishing-status, side-effect audit, and publishing tests prove external publishing remains blocked until human approval is attached to the execution envelope and audit operation/status are read through shared operation/response/status boundaries. | Bestanden | 2026-05-31 |
| T23 | GitHub adapter | GitHub adapter, connection-settings, direct operation registry, URL utility, HTTP-method, and adapter-result tests use a mocked GitHub API, resolve `git_ai-artist_codex_token` through the shared connection boundary, call shared operation and URL path validation directly, reject unsafe API paths and non-write methods before token reads, and confirm the token is read only by the adapter, not agents. | Bestanden | 2026-05-31 |
| T24 | Unit tests for safety service and policies | CI test suite runs canonicalizer, health-contract, request-metadata, sub-agent output-constructor, direct runtime interface-type imports, registry-driven connection settings/runtime env, canonical hashing/version tags/HMAC signatures/security-review serialization, direct source-ingestion hash/version and URL-domain boundaries, source-registry missing-row message contracts and optional lookup, execution-gate failure message contracts, request identity/trace IDs, runtime IDs, mapping utilities, cache request-kind/operation constants, cache/policy/execution reason messages, sub-agent statuses, mock-agent contracts, Knowledge Agent contracts and contextual snippets, ComfyUI contracts, review statuses, critic rubric vocabulary, Slack boundary helper usage, shared secret detection/redaction and file-scanning boundaries, direct gated-adapter operation constants, publishing operation/status boundaries, observability constants and redacted audit mappings, text utilities, Markdown heading utilities, direct numeric utility use at rubric boundaries, time utilities with direct-wrapper guard, payload fields/nested objects, response fields including first-choice message parsing, URL utilities with direct connector-boundary usage, HTTP method normalization, operation registry, direct model coercion at adapter/domain boundaries, classifier, OPA, cache, freshness, and audit unit tests with `--cov-fail-under=90` over the safety service modules. | Bestanden | 2026-05-31 |
| T25 | OpenClaw-to-safety integration tests | End-to-end test sends a request through OpenClaw hook, Safety Service, mock agents, validation, and final response synthesis. | Bestanden | 2026-05-31 |
| T26 | Observability | Telemetry, request-metadata, audit-redaction, and observability-constant tests verify trace ids, metrics, structured logs, stage constants, log-level constants, shared workspace/agent metadata mappings, and shared redacted mapping helpers are used for request, policy, cache, orchestration, and tool stages. | Bestanden | 2026-05-31 |
| T27 | Security review | Shared detection/redaction/file-scanning tests and security checklist tests scan logs, prompts, memory, audit payloads, artifacts, and canonical JSON serialization paths for secret patterns, assignment-style leaks, and policy bypasses. | Bestanden | 2026-05-31 |
| T28 | Production hardening and runbooks | Readiness, health-contract, and Markdown utility tests confirm runbooks, backups, restore check, env validation, centralized health-check expected signals, retention policy, incident contacts, and shared Markdown heading parsing exist. | Bestanden | 2026-05-31 |

## Required CI Gates

```text
docs-consistency:
  - scan for deprecated architecture terms
  - validate manifest links
  - validate tracker status totals

unit:
  - safety service
  - policy inputs and outputs
  - schema validation

integration:
  - OpenClaw hook to Safety Service
  - cache and source freshness
  - mock sub-agent orchestration

security:
  - secret redaction
  - default-deny write actions
  - execution envelope enforcement
```
