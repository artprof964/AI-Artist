---
name: karpathy-guidelines
description: Behavioral guidelines to reduce common LLM coding mistakes. Use when writing, reviewing, or refactoring code to avoid overcomplication, make surgical changes, surface assumptions, and define verifiable success criteria.
license: MIT
---

# Karpathy Guidelines

Behavioral guidelines to reduce common LLM coding mistakes, derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" -> "Write tests for invalid inputs, then make them pass"
- "Fix the bug" -> "Write a test that reproduces it, then make it pass"
- "Refactor X" -> "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```text
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

# Skill: local-ai-agent-system-latest-source

## Purpose

This project is a documentation-first blueprint for a local AI agent system.
It describes an orchestrated multi-agent architecture centered on a FastAPI
gateway, request canonicalization, OPA policy enforcement, a Hermes
orchestrator, restricted sub-agents, a safe read-only reuse path, and an
output tool agent.

## Short Overview

This repository is best understood as a system blueprint, not an implementation.
Its value is in defining boundaries: who receives requests, who enforces policy,
who orchestrates work, which agents stay restricted, and how outputs are safely
delivered.

## Project Context

- Primary source documents live in `docs/`.
- The existing design-specific skill note is
  `docs/local-ai-agent-system-design_latest_v2.skill.md`.
- This repository currently contains architecture, dependency, security,
  hardware, GitHub, and diagram documentation rather than runnable app code.

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

## Invariants

- Front Agent delegates only.
- Hermes owns routing, collection, validation, comparison, retries, and synthesis.
- Sub-agents return structured outputs to Hermes.
- OPA is the policy authority before reuse and before privileged execution.
- Cached reuse is limited to approved read-only responses.
- Output Tool Agent owns delivery to external channels.
- GitHub access uses `git_ai-artist_codex_token` from the environment.
- Hermes must never receive raw secrets.
- Actions should remain auditable.

## Stack Summary

- FastAPI
- OPA
- Hermes Agent
- vLLM or Ollama
- Qwen, Llama, or Mistral
- LlamaIndex
- Qdrant
- PostgreSQL
- MinIO
- Dagster
- Celery and Redis
- ComfyUI
- OpenBao
- Presidio
- OpenTelemetry, Loki, Prometheus, and Grafana

## Key Files

- `docs/overview_project_outline_params_latest_v2.md`
- `docs/local-ai-agent-system-design_latest_v2.skill.md`
- `docs/full_dependency_map_latest_v2.md`
- `docs/diagrams/latest_mermaid_flow_v2.md`
- `docs/diagrams/latest_interactive_flow_v2.html`
- `docs/hardware/hardware_requirements_latest_v2.md`
- `docs/github/github_integration_latest_v2.md`
- `docs/security/security_model_latest_v2.md`

## Guidance For Future Work

- Treat this repository as the authoritative architecture reference.
- Preserve the separation between gateway, policy, orchestration, sub-agents,
  and delivery.
- Keep secrets out of orchestration payloads.
- If runnable source code is added later, align it with the flow and invariants
  documented here and in `docs/`.
