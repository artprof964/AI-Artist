# Local AI Agent System - Latest Source Outline

## Optimized Core Flow

```text
External Request
 -> FastAPI Gateway
 -> OPA Policy Layer
 -> Front Agent
 -> Hermes Orchestrator
    -> route / assign
    -> delegate_task to restricted sub-agents
    -> sub-agents push structured outputs
    -> collect
    -> validate
    -> compare
    -> retry / escalate
    -> synthesize one result
    -> emit orchestrated output
 -> Final Validation
 -> Final Response / Action
 -> Output Tool Agent
 -> Channels / Platforms
```

## Invariants

```text
Front Agent delegates only.
Hermes Orchestrator owns route / assign / collect / validate / compare / retry / synthesize.
Sub-agents push structured outputs to Hermes.
OPA owns authority.
Output Tool Agent owns delivery.
GitHub token comes from Windows env variable git_ai-artist_codex_token.
Hermes never receives raw secrets.
All actions are auditable.
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
4. Hermes Orchestrator adapter
5. SubAgentOutput schema
6. mock sub-agents
7. Data Agent + RAG
8. Security Agent
9. Tool Agent
10. Media Agent + ComfyUI
11. Background Job Agent
12. Output Tool Agent
13. GitHub adapter
14. audit + observability
15. production hardening
```
