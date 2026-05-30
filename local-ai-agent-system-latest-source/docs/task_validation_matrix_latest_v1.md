# AI-Artist Task Validation Matrix

Every implementation task has a concrete validation test. Task status may move
to `Erledigt` only when the validation test passes and the related interface
contract is satisfied.

| ID | Task | Validation Test | Status | Finished |
|---|---|---|---|---|
| T01 | Stack decision: OpenClaw + hosted OpenAI LLM | Documentation scan confirms OpenClaw is the control plane, hosted OpenAI is the primary LLM, and deprecated architecture terms are absent. | Bestanden | 2026-05-30 |
| T02 | Project documentation and tracker alignment | Manifest includes all new docs, tracker dashboard totals match detail-plan status counts, and validation matrix exists. | Bestanden | 2026-05-30 |
| T03 | Repository scaffold | `pytest`, lint command, and a tree check confirm `backend/`, `workspaces/`, `policies/`, `tests/`, and `docker-compose.yml` exist. | Ausstehend |  |
| T04 | Docker Compose services | `docker compose config` succeeds and service health checks pass for PostgreSQL, Qdrant, MinIO, Redis, and OPA. | Ausstehend |  |
| T05 | FastAPI Safety Service endpoints | API tests call `/health`, `/v1/requests/canonicalize`, `/v1/requests/classify`, and `/v1/policy/evaluate` with expected schemas. | Ausstehend |  |
| T06 | OPA default-deny policies | Policy tests prove write, publish, delete, GitHub write, and cache replay are denied by default and allowed only with valid policy inputs. | Ausstehend |  |
| T07 | PostgreSQL migrations | Migration test applies schema from empty DB, verifies all query/source/cache/audit tables and indexes, then rolls back cleanly. | Ausstehend |  |
| T08 | OpenClaw AI-Artist workspace | Workspace test confirms required `SOUL.md`, `IDENTITY.md`, `USER.md`, `AGENTS.md`, `TOOLS.md`, `MEMORY.md`, and memory folders exist. | Ausstehend |  |
| T09 | Hosted OpenAI configuration | Smoke test loads model env vars, calls the hosted LLM with a redacted request, and records request id/model without logging secrets. | Ausstehend |  |
| T10 | OpenClaw safety-service tool hook | Integration test attempts a tool call and confirms Safety Service receives the pre-execution request before any adapter runs. | Ausstehend |  |
| T11 | `SubAgentOutput` schema | Schema tests accept valid agent outputs and reject missing status, malformed artifacts, invalid confidence, and unstructured errors. | Ausstehend |  |
| T12 | Mock sub-agents | Orchestration test routes one request through all mock agents, collects structured outputs, and synthesizes a single result. | Ausstehend |  |
| T13 | Approved read-only response cache | Cache tests verify only read responses with OPA approval and non-expired cache entries are replayed. | Ausstehend |  |
| T14 | Source freshness check | Freshness tests increment `source_data_registry.change_seq` and prove stale cached responses are blocked. | Ausstehend |  |
| T15 | Audit event log | Audit tests verify request, policy, reuse, execution-envelope, tool-call, and artifact events are persisted with correlation ids. | Ausstehend |  |
| T16 | Knowledge Agent retrieval | Retrieval test ingests sample source data, embeds it, queries Qdrant, and returns source-cited results through the Knowledge Agent. | Ausstehend |  |
| T17 | ComfyUI adapter behind execution gate | Adapter test proves image generation fails without a valid execution envelope and succeeds with a mocked approved envelope. | Ausstehend |  |
| T18 | Image provenance | Artifact test verifies prompt hash, workflow hash, model, seed, source refs, storage uri, and review status are stored for every image. | Ausstehend |  |
| T19 | Critic/Curator rubrics | Rubric test scores sample images or mocked image metadata and returns structured critique, pass/fail, and improvement notes. | Ausstehend |  |
| T20 | Slack development channel | Slack adapter test uses a mocked Slack API to confirm inbound request handling and outbound response formatting. | Ausstehend |  |
| T21 | Source ingestion | Ingestion test imports approved sample sources, stores snapshots, records source registry rows, and rejects disallowed source domains. | Ausstehend |  |
| T22 | Publishing Agent with human approval | Publishing test proves external publishing remains blocked until human approval is attached to the execution envelope. | Ausstehend |  |
| T23 | GitHub adapter | GitHub adapter test uses a mocked GitHub API and confirms `git_ai-artist_codex_token` is read only by the adapter, not agents. | Ausstehend |  |
| T24 | Unit tests for safety service and policies | CI test suite runs canonicalizer, classifier, OPA, cache, freshness, and audit unit tests with minimum coverage threshold. | Ausstehend |  |
| T25 | OpenClaw-to-safety integration tests | End-to-end test sends a request through OpenClaw hook, Safety Service, mock agents, validation, and final response synthesis. | Ausstehend |  |
| T26 | Observability | Telemetry test verifies trace ids, metrics, and structured logs are emitted for request, policy, cache, orchestration, and tool stages. | Ausstehend |  |
| T27 | Security review | Security checklist test scans logs, prompts, memory, audit payloads, and artifacts for secret patterns and policy bypasses. | Ausstehend |  |
| T28 | Production hardening and runbooks | Readiness test confirms runbooks, backups, restore check, env validation, health checks, retention policy, and incident contacts exist. | Ausstehend |  |

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
