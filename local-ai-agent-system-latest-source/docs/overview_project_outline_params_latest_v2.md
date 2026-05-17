# Local AI Agent System - Optimized Source Outline

## Optimized Core Flow

```text
External Request
 -> FastAPI Gateway
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
       -> Front Agent
       -> Hermes Orchestrator
          -> route / assign
          -> delegate_task to restricted sub-agents
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
Front Agent delegates only.
OPA is the authority both before reuse and before privileged execution.
Cached reuse is allowed only for approved read-only responses.
Source freshness must be checked before a cached response is replayed.
Hermes Orchestrator owns route / assign / collect / validate / compare / retry / synthesize.
Sub-agents push structured outputs to Hermes.
Output Tool Agent owns delivery and external execution.
GitHub token comes from Windows env variable git_ai-artist_codex_token.
Hermes never receives raw secrets.
Chat memory, agent memory, and persistent data storage remain separate concerns.
All actions and cache reuses are auditable.
```

## Open-Source Stack

```text
FastAPI
OPA
Hermes Agent
vLLM / Ollama
Qwen / Llama / Mistral
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
Docker Compose first, k3s later
GitHub API via Tool Agent
```

## Build Order

```text
1. FastAPI health endpoint
2. PostgreSQL / Qdrant / MinIO / Redis
3. OPA base policies
4. request canonicalizer + policy context builder
5. Hermes Orchestrator adapter
6. SubAgentOutput schema
7. mock sub-agents
8. source registry + persistent data storage + source data ingestion
9. query source tracking table + indexes
10. repeat-query reuse gate behind OPA
11. Data Agent + RAG
12. Security Agent
13. Tool Agent
14. Media Agent + ComfyUI
15. Background Job Agent
16. execution policy gate
17. Output Tool Agent
18. GitHub adapter
19. audit + observability
20. production hardening
```
