# AI-Artist Agent System - Optimized Source Outline

## Selected Direction

```text
Agent control plane: OpenClaw
Primary LLM backend: provider-neutral LLM API
Primary model lane: provider-primary-model, with provider fallback / classifier for cost-controlled paths
Image generation: ComfyUI with Flux / SDXL
Safety layer: FastAPI + OPA + PostgreSQL audit/cache/source tracking
```

## Optimized Core Flow

```text
External Request
 -> OpenClaw Gateway
 -> AI-Artist Main Agent
 -> FastAPI Safety Service
 -> Request Canonicalizer
 -> Policy Context Builder
 -> OPA Policy Layer
 -> Request Classifier
    -> repeat read-only query
       -> Reuse Gate
       -> Source Freshness Check
       -> Approved Response Cache
       -> Final Validation
       -> Final Response / Action
    -> fresh query or action request
       -> OpenClaw Main Agent
       -> OpenClaw Agent Runtime
          -> route / assign
          -> delegate_task to restricted OpenClaw sub-agents
          -> collect structured outputs
          -> validate
          -> compare
          -> retry / escalate
          -> synthesize one result
       -> Final Validation
       -> Execution Policy Gate
       -> Output Tool Agent
       -> Channels / Platforms
```

## Invariants

```text
AI-Artist Main Agent delegates specialized work and does not bypass policy gates.
OPA is the authority both before reuse and before privileged execution.
Cached reuse is allowed only for approved read-only responses.
Source freshness must be checked before a cached response is replayed.
OpenClaw Agent Runtime owns route / assign / collect / validate / compare / retry / synthesize.
Sub-agents push structured outputs to the main agent runtime.
Output Tool Agent owns delivery and external execution.
GitHub token comes from Windows env variable git_ai-artist_codex_token.
OpenClaw agents never receive raw secrets.
Chat memory, agent memory, and persistent data storage remain separate concerns.
All actions and cache reuses are auditable.
Every implementation task has a validation test before it can be marked done.
```

## Standard Interface Process

```text
1. Intake: OpenClaw receives request and loads workspace context.
2. Normalize: FastAPI Safety Service creates request fingerprint.
3. Classify: request becomes read, action, or mixed.
4. Policy Check: Safety Service asks OPA for continuation/reuse permission.
5. Reuse Decision: read-only repeat requests check cache and source freshness.
6. Orchestrate: OpenClaw routes fresh work to restricted sub-agents.
7. Validate: runtime validates SubAgentOutput and synthesizes one result.
8. Execution Gate: privileged actions require signed execution envelope.
9. Deliver: Output Tool Agent executes approved delivery.
10. Audit: request, policy, reuse, tool, and artifact events are recorded.
```

## Open-Source Stack

```text
OpenClaw Gateway
OpenClaw workspace files: SOUL.md, IDENTITY.md, USER.md, AGENTS.md, TOOLS.md, MEMORY.md
provider-neutral LLM API
FastAPI safety service
OPA
provider primary / fallback / classifier model lanes
LlamaIndex
Qdrant
PostgreSQL
MinIO
Dagster
Celery + Redis
ComfyUI
Request canonicalizer
Policy context builder
Approved response cache for repeated safe queries
Query source tracking table with change detection indexes
Persistent data storage for source data, vectors, metadata, and artifacts
OpenBao
Presidio
OpenTelemetry + Loki + Prometheus + Grafana
Docker Compose first, k3s later if scaling requires it
GitHub API via Tool Agent
```

## Build Order

```text
1. Repository scaffold + Docker Compose
2. OpenClaw AI-Artist workspace skeleton
3. provider-neutral LLM API configuration + smoke test
4. FastAPI safety service health endpoint
5. request canonicalizer + policy context builder
6. OPA base policies
7. PostgreSQL / Qdrant / MinIO / Redis
8. query source tracking table + indexes
9. OpenClaw tool hook for safety-service checks
10. SubAgentOutput schema
11. mock sub-agents
12. source registry + persistent data storage + source data ingestion
13. repeat-query reuse gate behind OPA
14. Knowledge Agent + RAG
15. Security Agent
16. Tool Agent
17. Image-Gen Agent + ComfyUI
18. Background Job Agent
19. execution policy gate
20. Output Tool Agent
21. GitHub adapter
22. Slack integration
23. audit + observability
24. production hardening
```

## Validation Rule

```text
Each build-order item maps to one or more validation tests in
task_validation_matrix_latest_v1.md. CI must include docs-consistency, unit,
integration, and security gates before production hardening.
```

## Current Project Status

```text
See project_status_latest_v1.md for the latest status snapshot.
Current implementation state: all tracker tasks T01 through T28 passed.
Next task: operate from the production runbook and maintain validation gates.
```
