# Skill: ai-artist-openclaw-llm-api-system-design

## Selected Stack

```text
OpenClaw Gateway and workspace files are the agent control plane.
provider-neutral LLM API is the primary LLM backend.
FastAPI + OPA + PostgreSQL provide local safety, cache, source tracking, and audit.
ComfyUI provides image generation.
Every implementation task has a validation test recorded in the tracker and in
`docs/task_validation_matrix_latest_v1.md`.
```

## Mandatory Flow

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
       -> restricted sub-agents
       -> validation / compare / retry / synthesize
       -> Final Validation
       -> Execution Policy Gate
       -> Output Tool Agent
       -> Channels / Platforms
```

## Rules

```text
- AI-Artist Main Agent delegates specialized work and does not bypass policy gates.
- OPA is checked before reuse and before privileged execution.
- Cached reuse is allowed only for approved read-only responses.
- Source freshness must be checked before cache replay.
- OpenClaw owns orchestration and loop control.
- Sub-agents push structured outputs to the main OpenClaw runtime.
- Output Tool Agent owns delivery.
- LLM API access uses deepseek-open-art from environment.
- GitHub access uses git_ai-artist_codex_token from environment.
- OpenClaw agents never see raw secrets.
- Standard interfaces are defined in `docs/interface_process_standard_latest_v1.md`.
- Task validation tests are defined in `docs/task_validation_matrix_latest_v1.md`.
```
