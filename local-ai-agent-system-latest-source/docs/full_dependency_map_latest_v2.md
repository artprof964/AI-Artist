# Latest Dependency Map

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

## Runtime

```text
FastAPI
 |- OPA client
 |- Front Agent
 |- Hermes Orchestrator
 `- Output Tool Agent

Hermes Orchestrator
 |- delegate_task wrapper
 |- sub-agent registry
 |- output schema validator
 |- retry/escalation policy
 `- synthesis step

Output Tool Agent
 |- email adapter
 |- chat adapter
 |- webhook adapter
 |- file/storage adapter
 |- dashboard adapter
 `- GitHub adapter
```

## Data

```text
Data Agent -> LlamaIndex -> Qdrant -> PostgreSQL metadata -> MinIO files
Background Job Agent -> Dagster -> Celery -> Redis -> embeddings -> Qdrant
Media Agent -> ComfyUI -> GPU worker -> MinIO output -> PostgreSQL metadata
```

## Secrets

```text
GitHub Adapter -> os.environ["git_ai-artist_codex_token"]
Production later -> OpenBao runtime injection
```
