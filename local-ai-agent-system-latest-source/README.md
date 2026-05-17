# Local AI Agent System Overview

## Short Overview

This folder is a documentation-first architecture pack for a local AI agent
system. The optimized model now separates four concerns more explicitly:

- request normalization and policy context building
- safe reuse of repeated read-only queries
- orchestrated multi-agent execution for fresh or complex work
- policy-gated external execution for writes and irreversible actions

## What Is In This Folder

- `SKILL.md`: project guidance and operating rules
- `docs/overview_project_outline_params_latest_v2.md`: concise architecture outline
- `docs/full_dependency_map_latest_v2.md`: runtime, data, memory, cache, and secret map
- `docs/query_source_tracking_schema_latest_v1.md`: PostgreSQL tracking schema for source freshness and repeated-query reuse
- `docs/diagrams/latest_mermaid_flow_v3.md`: full Mermaid chart of the optimized architecture
- `docs/diagrams/latest_interactive_flow_v3.html`: interactive architecture explorer
- `docs/security/security_model_latest_v2.md`: trust boundaries and approval rules

## Optimized Architecture

```text
External Request
 -> FastAPI Gateway
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
       -> Front Agent
       -> Hermes Orchestrator
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

The system is still a blueprint rather than running code. The most important
implementation targets are:

- canonical request normalization
- policy context building and OPA evaluation
- source registry with monotonic change index
- repeated-query reuse gate with read-only cache policy
- orchestrator and sub-agent contracts
- execution gate for tool and write actions
- audit and observability around both cache reuse and fresh execution
