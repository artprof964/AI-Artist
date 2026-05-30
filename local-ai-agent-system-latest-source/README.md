# AI-Artist OpenClaw Agent System Overview

## Short Overview

This folder is a documentation-first architecture pack for the AI-Artist
agent system. The implementation direction is now fixed: **OpenClaw** is the
agent control plane, and a **hosted OpenAI LLM** is the primary reasoning
backend. The optimized model separates four concerns explicitly:

- request normalization and policy context building
- safe reuse of repeated read-only queries
- OpenClaw-orchestrated multi-agent execution for fresh or complex work
- policy-gated external execution for writes and irreversible actions

## What Is In This Folder

- `SKILL.md`: project guidance and operating rules
- `docs/overview_project_outline_params_latest_v2.md`: concise architecture outline
- `docs/implementation_stack_openclaw_hosted_llm_latest_v1.md`: selected implementation stack
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

The system is still a blueprint rather than running code. Current status is
tracked in `docs/project_status_latest_v1.md`. The next implementation targets
are:

- OpenClaw workspace skeleton for AI-Artist
- hosted OpenAI configuration and smoke test
- FastAPI safety service
- standardized OpenClaw-to-Safety-Service interfaces
- task-level validation tests and CI gates
- canonical request normalization
- policy context building and OPA evaluation
- source registry with monotonic change index
- repeated-query reuse gate with read-only cache policy
- OpenClaw agent contracts and workspace files
- execution gate for tool and write actions
- audit and observability around both cache reuse and fresh execution

## Standard Process

All implementation work follows the process in
`docs/interface_process_standard_latest_v1.md`: intake, normalize, classify,
policy check, reuse decision, orchestrate, validate, execution gate, deliver,
and audit. Every task in the tracker must keep its validation test aligned with
`docs/task_validation_matrix_latest_v1.md`.
