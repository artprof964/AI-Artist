# Skill: local-ai-agent-system-design

## Mandatory Flow

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
       -> restricted sub-agents
       -> validation / compare / retry / synthesize
       -> Final Validation
       -> Execution Policy Gate
       -> Output Tool Agent
       -> Channels / Platforms
```

## Rules

```text
- Front Agent delegates only.
- OPA is checked before reuse and before privileged execution.
- Cached reuse is allowed only for approved read-only responses.
- Source freshness must be checked before cache replay.
- Hermes owns orchestration and loop control.
- Sub-agents push structured outputs to Hermes.
- Output Tool Agent owns delivery.
- GitHub access uses git_ai-artist_codex_token from environment.
- Hermes never sees raw secrets.
```
