# AI-Artist OpenClaw Agent System Overview

## Short Overview

This folder is a documentation-first architecture pack for the AI-Artist
agent system. The implementation direction is now fixed: **OpenClaw** is the
agent control plane, and a **provider-neutral LLM API** is the primary reasoning
backend. The optimized model separates four concerns explicitly:

- request normalization and policy context building
- safe reuse of repeated read-only queries
- OpenClaw-orchestrated multi-agent execution for fresh or complex work
- policy-gated external execution for writes and irreversible actions

## What Is In This Folder

- `SKILL.md`: project guidance and operating rules
- `docs/overview_project_outline_params_latest_v2.md`: concise architecture outline
- `docs/implementation_stack_openclaw_llm_api_latest_v1.md`: selected implementation stack
- `docs/interface_process_standard_latest_v1.md`: standardized interfaces, request envelopes, and delivery process
- `docs/task_validation_matrix_latest_v1.md`: validation test for each implementation task
- `docs/project_status_latest_v1.md`: latest status, next implementation slice, and alignment check
- `docs/full_dependency_map_latest_v2.md`: runtime, data, memory, cache, and secret map
- `docs/query_source_tracking_schema_latest_v1.md`: PostgreSQL tracking schema for source freshness and repeated-query reuse
- `docs/diagrams/latest_mermaid_flow_v3.md`: full Mermaid chart of the optimized architecture
- `docs/diagrams/latest_interactive_flow_v3.html`: interactive architecture explorer
- `docs/security/security_model_latest_v2.md`: trust boundaries and approval rules

## Optimized Architecture

```text
External Request
 -> OpenClaw Gateway
 -> AI-Artist Main Agent
 -> FastAPI Safety Service
 -> Request Canonicalizer
 -> Policy Context Builder
 -> OPA Policy Layer
 -> Request Classifier
    -> read-only repeat query
       -> Reuse Gate
       -> Source Freshness Check
       -> Approved Response Cache
       -> Final Validation
       -> Final Response
    -> fresh query or action request
       -> OpenClaw Main Agent
       -> OpenClaw Agent Runtime
       -> Restricted Sub-Agents
       -> Validation / Compare / Retry / Synthesis
       -> Final Validation
       -> Execution Policy Gate
       -> Output Tool Agent
       -> Channels / Platforms
```

## Key Improvements

- Repeated-query reuse no longer happens on a vague cache hit. It now depends on:
  - normalized request fingerprint
  - requester and policy scope
  - OPA approval
  - source freshness check
  - read-only response classification
- Action requests are separated from reusable read-only responses.
- External execution is gated again before delivery, not just at entry.
- Source freshness is designed around indexed change sequences instead of only
  comparing timestamps or hashes row by row.
- Chat memory, agent working memory, and persistent storage are treated as
  distinct layers with different security expectations.

## Delivery Readiness

The system has a complete validated local backend implementation. Current
status is tracked in `docs/project_status_latest_v1.md`.

The OPA default-deny policy tests, PostgreSQL migration validation,
OpenClaw AI-Artist workspace validation, provider-neutral LLM API smoke validation,
OpenClaw safety-service hook validation, SubAgentOutput schema validation, and
mock sub-agent orchestration validation, approved read-only response cache
validation, source freshness validation, audit event log validation,
Knowledge Agent retrieval validation, ComfyUI adapter execution-gate validation,
image provenance validation, Critic/Curator rubric validation, Slack development
channel validation, source ingestion validation, publishing approval validation,
GitHub adapter validation, unit CI coverage gate validation, OpenClaw-to-safety
integration validation, observability validation, security review validation,
and production readiness validation are implemented and passed as T06 through
T28.

## Standard Process

All implementation work follows the process in
`docs/interface_process_standard_latest_v1.md`: intake, normalize, classify,
policy check, reuse decision, orchestrate, validate, execution gate, deliver,
and audit. Every task in the tracker must keep its validation test aligned with
`docs/task_validation_matrix_latest_v1.md`.
