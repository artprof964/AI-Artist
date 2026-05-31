# AI-Artist Implementation Stack - OpenClaw + LLM API

## Decision

The project will implement AI-Artist on **OpenClaw** as the agent control
plane and use a **provider-neutral LLM API** as the primary reasoning backend.

This resolves the previous architecture split:

- OpenClaw owns agent runtime, workspace bootstrap files, channel adapters,
  agent sessions, and tool invocation.
- Provider-neutral LLM API models own language reasoning, planning, critique, and
  multimodal analysis.
- ComfyUI owns image generation and post-processing.
- FastAPI, PostgreSQL, OPA, and the cache/freshness layer become a local
  safety, persistence, and orchestration support service around OpenClaw.

## Selected configured model lane

```text
Primary reasoning model:      Provider primary model
Cost-controlled fallback:     provider-fallback-model
Fast classification model:    provider-classifier-model or equivalent small configured model
Embeddings:                   provider-embedding-model by default
Moderation / safety:          provider moderation endpoint plus local policy checks
Image generation:             ComfyUI with Flux / SDXL locally or on GPU cloud
```

Use the provider-neutral LLM API for agentic and reasoning calls. Keep model names
in runtime configuration so the stack can move forward without code changes.

## Full Inline Stack

```text
User / Channel
  -> OpenClaw Gateway
     -> OpenClaw workspace loader
        -> SOUL.md
        -> IDENTITY.md
        -> USER.md
        -> AGENTS.md
        -> TOOLS.md
        -> MEMORY.md / memory/
     -> channel adapter
        -> Slack first
        -> local CLI / web chat for development
        -> social publishing adapters later
     -> AI-Artist Main Agent
        -> provider-neutral LLM API
        -> local safety service
           -> request canonicalizer
           -> policy context builder
           -> OPA policy check
           -> request classifier
           -> read-only reuse gate
           -> source freshness check
           -> execution policy gate
           -> audit logger
        -> agent registry
           -> Social Scout Agent
           -> Image-Gen Agent
           -> Critic / Curator Agent
           -> Knowledge Agent
           -> Publishing Agent
           -> Audit Agent
        -> tool adapters
           -> ComfyUI adapter
           -> GitHub adapter
           -> storage adapter
           -> Slack adapter
           -> web/source ingestion adapter
           -> metrics adapter
  -> final response, image artifact, scheduled job, or gated external action
```

## Standard Interfaces

All component handoffs use the contracts in
`interface_process_standard_latest_v1.md`.

```text
OpenClaw Gateway -> FastAPI Safety Service
  /v1/requests/canonicalize
  /v1/requests/classify
  /v1/policy/evaluate
  /v1/reuse/check
  /v1/execution/envelope
  /v1/audit/events

FastAPI Safety Service -> OPA
  policy input: request_kind, operation, requester_scope, policy_scope,
  freshness state, approval requirement

OpenClaw Runtime -> Sub-Agents
  task payload in
  SubAgentOutput out

Output Tool Agent -> External Adapters
  signed execution envelope required for writes
```

## Runtime Components

```text
OpenClaw Gateway
  - selected control plane
  - owns agent sessions and workspace loading
  - reads SOUL.md, AGENTS.md, TOOLS.md, memory files, and channel config

LLM API Provider
  - LLM API primary
  - API keys injected through environment variables only
  - no raw secrets in prompts, logs, memory, or agent payloads

Local Safety Service
  - FastAPI
  - exposes internal endpoints for policy, classification, audit, cache,
    source freshness, and execution envelopes
  - called by OpenClaw tool hooks or adapters before sensitive actions

OPA
  - policy authority for reuse and privileged execution
  - denies writes by default unless an approved execution envelope exists

PostgreSQL
  - query_request_run
  - source_data_registry
  - query_request_source_dependency
  - query_request_dependency_snapshot
  - approved_response_cache
  - audit_event

Qdrant
  - vector search for knowledge base, style library, and source summaries

MinIO
  - generated images
  - source snapshots
  - response artifacts
  - ComfyUI outputs

Redis
  - queues, locks, rate-limit counters, and transient job state

Celery / Dagster
  - background ingestion
  - scheduled trend scans
  - embeddings
  - image generation jobs
  - cleanup and retention jobs

ComfyUI
  - Flux / SDXL workflows
  - ControlNet / IP-Adapter workflows when approved
  - runs on local GPU or GPU cloud worker

Observability
  - OpenTelemetry traces
  - Prometheus metrics
  - Loki logs
  - Grafana dashboards
```

## Agent Workspaces

```text
workspaces/
  ai-artist-main/
    SOUL.md
    IDENTITY.md
    USER.md
    AGENTS.md
    TOOLS.md
    MEMORY.md
    memory/
      style_principles.md
      safety_rules.md
      prompt_patterns.md

  social-scout/
    SOUL.md
    AGENTS.md
    TOOLS.md
    memory/

  image-gen/
    SOUL.md
    AGENTS.md
    TOOLS.md
    comfyui_workflows/

  critic-curator/
    SOUL.md
    AGENTS.md
    TOOLS.md
    rubrics/
```

## Development Environment

```text
Node.js 20+                 OpenClaw runtime
Python 3.11+                FastAPI, workers, ingestion, tests
Docker Compose              local services
PostgreSQL                  relational state and audit
Qdrant                      vector store
MinIO                       object storage
Redis                       queue/cache/locks
OPA                         policy engine
ComfyUI                     image workflow engine
GitHub Actions              CI
pytest                      Python tests
ruff                        Python linting
mypy                        Python type checks where useful
```

## Environment Variables

`deepseek-open-art` is the standard project key for LLM API access. It maps to
the DeepSeek-compatible endpoint below and replaces provider-specific key names
in setup, readiness checks, and live smoke tests. `DEEPSEEK_API_KEY` remains a
loader-only legacy alias for old local shells.

```text
deepseek-open-art=...
LLM_API_URL=https://api.deepseek.com
LLM_PRIMARY_MODEL=deepseek-v4-pro
LLM_FALLBACK_MODEL=provider-fallback-model
LLM_CLASSIFIER_MODEL=provider-classifier-model
LLM_EMBEDDING_MODEL=provider-embedding-model

OPENCLAW_WORKSPACE_ROOT=./workspaces
OPENCLAW_GATEWAY_URL=http://localhost:18789

DATABASE_URL=postgresql://ai_artist:ai_artist@localhost:5432/ai_artist
QDRANT_URL=http://localhost:6333
MINIO_ENDPOINT=http://localhost:9000
REDIS_URL=redis://localhost:6379/0
OPA_URL=http://localhost:8181
COMFYUI_URL=http://localhost:8188

SLACK_BOT_TOKEN=...
git_ai-artist_codex_token=...
```

## MVP Implementation Order

```text
1. Repository scaffold and local Docker Compose.
2. OpenClaw workspace skeleton for AI-Artist Main Agent.
3. provider-neutral LLM API configuration and smoke test.
4. FastAPI safety service with health, canonicalize, classify, and policy endpoints.
5. OPA default-deny policies for write actions and cache reuse.
6. PostgreSQL migrations for query/source/cache/audit tables.
7. OpenClaw tool hook that calls the safety service before tool execution.
8. Mock Social Scout, Image-Gen, Critic, Knowledge, and Publishing agents.
9. ComfyUI adapter behind execution policy gate.
10. Slack development channel integration.
11. Source ingestion and Qdrant-backed knowledge retrieval.
12. Approved read-only response cache and source freshness checks.
13. Observability dashboard and runbooks.
14. Production hardening.
```

## Validation Standard

Every MVP task must include a validation test before implementation begins.
The canonical validation list lives in `task_validation_matrix_latest_v1.md`.
The tracker mirrors each task's validation test so project status can be
audited without opening source code.

## Optimization Notes

- Keep the first slice narrow: one OpenClaw main workspace, one configured model
  call, one safety service, one policy gate, and one mocked image task.
- Do not wire social APIs before the policy and audit path exists.
- Treat generated images as artifacts with provenance: prompt, model, workflow,
  seed, source references, and reviewer decision.
- Use LLM APIs for quality and speed now; add local LLM fallback later only
  after the control plane and cache economics are visible.
- Make every external write action require a signed execution envelope.
