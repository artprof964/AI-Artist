# Latest Dependency Map

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
       -> Final Response
    -> fresh query or action request
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
       -> Final Validation
       -> Execution Policy Gate
       -> Output Tool Agent
       -> Channels / Platforms
```

## Runtime

```text
FastAPI
 |- request canonicalizer
 |- policy context builder
 |- OPA client
 |- request classifier
 |- reuse gate
 |- source freshness check
 |- Front Agent
 |- Hermes Orchestrator
 `- Output Tool Agent

Hermes Orchestrator
 |- delegate_task wrapper
 |- sub-agent registry
 |- output schema validator
 |- retry / escalation policy
 `- synthesis step

Execution Policy Gate
 |- action classification
 |- OPA recheck for privileged execution
 |- human approval routing
 `- signed execution envelope to Tool / Output agents

Output Tool Agent
 |- email adapter
 |- chat adapter
 |- webhook adapter
 |- file/storage adapter
 |- dashboard adapter
 `- GitHub adapter
```

## Data And Memory

```text
Source Data -> source_data_registry -> Data Agent -> LlamaIndex -> Qdrant -> PostgreSQL metadata -> MinIO files
Background Job Agent -> Dagster -> Celery -> Redis -> embeddings -> Qdrant
Media Agent -> ComfyUI -> GPU worker -> MinIO output -> PostgreSQL metadata
Persistent Data Storage -> Qdrant + PostgreSQL metadata + MinIO files + MinIO output
Chat Memory -> session / thread context
Agent Working Memory -> Hermes state + bounded sub-agent task state
Approved Response Cache -> repeated approved read-only responses
Query Source Tracking Tables -> request fingerprint + dependency set + change detection
```

## Source Freshness And Reuse

```text
Normalized request fingerprint -> requester scope + policy scope
 -> last completed matching run
 -> dependency set lookup
 -> compare stored source_change_seq_at_run against current source_data_registry.change_seq
 -> if unchanged and OPA allows: approved cache replay
 -> else: continue to fresh orchestration
```

## Secrets

```text
GitHub Adapter -> os.environ["git_ai-artist_codex_token"]
Production later -> OpenBao runtime injection
Secrets never enter chat memory, agent memory, prompts, logs, or audit payloads
```

## Speed Optimization Rules

```text
Repeated queries may use a fast path only after OPA policy evaluation.
Only read-only responses are eligible for cache replay.
Cache keys must use normalized request fingerprints plus requester / policy scope.
Source freshness must be checked before replay using indexed change sequences.
Cache invalidation and TTL must prevent stale or unauthorized reuse.
Privileged execution must still pass an execution policy gate even after synthesis.
```
