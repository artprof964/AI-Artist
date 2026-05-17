# Skill: local-ai-agent-system-design

## Mandatory Flow

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

## Rules

```text
- Front Agent delegates only.
- Hermes owns sub-agent routing and loop control.
- Sub-agents push structured outputs to Hermes.
- OPA is external authority.
- Output Tool Agent owns delivery.
- GitHub access uses git_ai-artist_codex_token from environment.
- Hermes never sees raw secrets.
```
