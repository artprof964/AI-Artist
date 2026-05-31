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
| T05 | FastAPI Safety Service endpoints | API tests call `/health`, `/v1/requests/canonicalize`, `/v1/requests/classify`, and `/v1/policy/evaluate` with expected schemas. | Bestanden | 2026-05-31 |
| T06 | OPA default-deny policies | Policy tests prove write, publish, delete, GitHub write, and cache replay are denied by default and allowed only with valid policy inputs. | Bestanden | 2026-05-31 |
| T07 | PostgreSQL migrations | Migration test applies schema from empty DB, verifies all query/source/cache/audit tables and indexes, then rolls back cleanly. | Bestanden | 2026-05-31 |
| T08 | OpenClaw AI-Artist workspace | Workspace test confirms required `SOUL.md`, `IDENTITY.md`, `USER.md`, `AGENTS.md`, `TOOLS.md`, `MEMORY.md`, and memory folders exist. | Bestanden | 2026-05-31 |
| T09 | Provider-neutral LLM API configuration | Smoke test loads DeepSeek model env vars, calls the OpenAI-compatible LLM API with a redacted request, and records response id/model/content without logging secrets. | Bestanden | 2026-05-31 |
| T10 | OpenClaw safety-service tool hook | Integration test attempts a tool call and confirms Safety Service receives the pre-execution request before any adapter runs. | Bestanden | 2026-05-31 |
| T11 | `SubAgentOutput` schema | Schema tests accept valid agent outputs and reject missing status, malformed artifacts, invalid confidence, and unstructured errors. | Bestanden | 2026-05-31 |
| T12 | Mock sub-agents | Orchestration test routes one request through all mock agents, collects structured outputs, and synthesizes a single result. | Bestanden | 2026-05-31 |
| T13 | Approved read-only response cache | Cache tests verify only read responses with OPA approval and non-expired cache entries are replayed. | Bestanden | 2026-05-31 |
| T14 | Source freshness check | Freshness tests increment `source_data_registry.change_seq` and prove stale cached responses are blocked. | Bestanden | 2026-05-31 |
| T15 | Audit event log | Audit tests verify request, policy, reuse, execution-envelope, tool-call, and artifact events are persisted with correlation ids. | Bestanden | 2026-05-31 |
| T16 | Knowledge Agent retrieval | Retrieval test ingests sample source data, embeds it, queries Qdrant, returns source-cited results through the Knowledge Agent, and excludes unapproved sources. | Bestanden | 2026-05-31 |
| T17 | ComfyUI adapter behind execution gate | Adapter test proves image generation fails without a valid execution envelope and succeeds with a mocked approved envelope. | Bestanden | 2026-05-31 |
| T18 | Image provenance | Artifact test verifies prompt hash, workflow hash, model, seed, source refs, storage uri, and review status are stored for every image. | Bestanden | 2026-05-31 |
| T19 | Critic/Curator rubrics | Rubric test scores sample images or mocked image metadata and returns structured critique, pass/fail, and improvement notes. | Bestanden | 2026-05-31 |
| T20 | Slack development channel | Slack adapter test uses a mocked Slack API to confirm inbound request handling and outbound response formatting. | Bestanden | 2026-05-31 |
| T21 | Source ingestion | Ingestion test imports approved sample sources, stores snapshots, records source registry rows, and rejects disallowed source domains. | Bestanden | 2026-05-31 |
| T22 | Publishing Agent with human approval | Publishing test proves external publishing remains blocked until human approval is attached to the execution envelope. | Bestanden | 2026-05-31 |
| T23 | GitHub adapter | GitHub adapter test uses a mocked GitHub API and confirms `git_ai-artist_codex_token` is read only by the adapter, not agents. | Bestanden | 2026-05-31 |
| T24 | Unit tests for safety service and policies | CI test suite runs canonicalizer, classifier, OPA, cache, freshness, and audit unit tests with `--cov-fail-under=90` over the safety service modules. | Bestanden | 2026-05-31 |
| T25 | OpenClaw-to-safety integration tests | End-to-end test sends a request through OpenClaw hook, Safety Service, mock agents, validation, and final response synthesis. | Bestanden | 2026-05-31 |
| T26 | Observability | Telemetry test verifies trace ids, metrics, and structured logs are emitted for request, policy, cache, orchestration, and tool stages. | Bestanden | 2026-05-31 |
| T27 | Security review | Security checklist test scans logs, prompts, memory, audit payloads, and artifacts for secret patterns and policy bypasses. | Bestanden | 2026-05-31 |
| T28 | Production hardening and runbooks | Readiness test confirms runbooks, backups, restore check, env validation, health checks, retention policy, and incident contacts exist. | Bestanden | 2026-05-31 |

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
