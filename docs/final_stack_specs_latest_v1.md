# AI-Artist Final Stack Specs - Latest

## Status

```text
Date: 2026-05-31
Implementation status: all 28 tracker tasks complete
Final validation: 192 passed, 1 skipped, 1 warning
Skipped test: live provider-neutral LLM API smoke test requires deepseek-open-art
Lint: ruff all checks passed
```

## Selected Stack

```text
Agent control plane: OpenClaw workspace files and safety hook contracts
LLM backend: provider-neutral LLM API
Safety service: FastAPI
Policy authority: OPA default-deny policy
Persistence: PostgreSQL query/source/cache/audit schema
Vector store: Qdrant
Object/artifact store: MinIO
Transient state: Redis
Image execution path: ComfyUI adapter behind execution envelope gate
Local orchestration tests: deterministic mock sub-agents
Production readiness: local runbook, env schema, health, backup, restore, retention, contacts
```

## Runtime Services

```text
PostgreSQL 16: query_request_run, source_data_registry, dependency snapshots,
approved_response_cache, audit_event.

Redis 7: queue and transient state placeholder for later async workers.

Qdrant: vector retrieval path for Knowledge Agent tests.

MinIO: artifact/object storage target for generated images and source snapshots.

OPA 0.70.0: default-deny policy for reuse and privileged execution.

FastAPI Safety Service: request canonicalization, classification, local policy
evaluation, execution-envelope signing, audit event recording.
```

## Backend Modules

```text
backend/app.py: FastAPI endpoints.
backend/service.py: canonicalization, classification, local policy gate, execution envelope.
backend/schemas.py: API and SubAgentOutput schemas.
backend/adapter_results.py: shared gated adapter result field mapping.
backend/secret_redaction.py: shared secret-key and token-shape redaction utilities.
backend/audit.py: in-memory audit repository and recursive secret redaction.
backend/execution_gate.py: shared execution-envelope coercion and validation for gated adapters.
backend/response_cache.py: approved read-only response cache.
backend/source_freshness.py: dependency snapshot and stale-source checks.
backend/source_ingestion.py: approved local source ingestion and domain/scheme rejection.
backend/connection_settings.py: shared env var names, defaults, aliases, and connection settings loader.
backend/llm_api_smoke.py: provider-neutral LLM API configuration and redacted smoke request path.
backend/openclaw_hook.py: pre-tool Safety Service hook.
backend/orchestrator.py: mock sub-agent routing and synthesis.
backend/knowledge.py: deterministic source-cited retrieval.
backend/comfyui_adapter.py: execution-envelope-gated image generation adapter.
backend/image_provenance.py: prompt/workflow hashing and provenance records.
backend/critic_curator.py: deterministic image critique rubric.
backend/slack_adapter.py: mocked Slack request/response adapter.
backend/publishing.py and backend/publishing_adapter.py: approval-gated publishing path.
backend/github_adapter.py: GitHub write adapter with token isolated to adapter boundary.
backend/observability.py: traces, metrics, structured logs, redaction.
backend/security_review.py: deterministic security checklist helpers.
backend/readiness.py: production readiness schema and runbook validators.
```

## Interfaces

```text
GET  /health
POST /v1/requests/canonicalize
POST /v1/requests/classify
POST /v1/policy/evaluate
POST /v1/execution/envelope
POST /v1/audit/events
GET  /v1/audit/events/{correlation_id}
```

## Security Invariants

```text
OPA default allow remains false.
Read-only reuse requires read classification, OPA approval, non-expired cache,
matching requester/policy scope, and unchanged source dependencies.
Write, publish, delete, GitHub write, and image generation are denied until a
valid operation-matching execution envelope exists.
External publish/write paths require human approval.
OpenClaw agents, prompts, logs, audit payloads, and memory files must not
contain raw API keys, OAuth tokens, Slack tokens, GitHub tokens, signing keys, or
private webhook secrets.
Connection names, defaults, and secret aliases must be changed through
backend/connection_settings.py before adapter-specific code.
Execution-envelope validation must flow through backend/execution_gate.py before
adapter-specific side-effect logic.
Secret redaction patterns and replacement behavior must flow through
backend/secret_redaction.py before adapter-specific logging or response shaping.
Gated adapter result envelope fields must flow through backend/adapter_results.py
before adapter-specific return dataclasses add extra fields.
Generated image provenance stores prompt_hash and workflow_hash, not raw prompt
text in stored records.
```

## Validation Matrix Summary

```text
T01-T02: stack decision and tracker/docs alignment
T03-T07: repository scaffold, compose stack, Safety Service, OPA, PostgreSQL schema
T08-T12: OpenClaw workspace, provider-neutral LLM API config, safety hook, schemas, mock agents
T13-T15: response cache, source freshness, audit log
T16-T19: retrieval, ComfyUI gate, image provenance, critic/curator
T20-T23: Slack, source ingestion, publishing approval, GitHub adapter
T24-T26: unit CI coverage, OpenClaw-to-safety integration, observability
T27-T28: security review and production readiness
```

## Operating Commands

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
docker compose up -d postgres redis qdrant minio opa
docker compose ps
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check .
powershell -ExecutionPolicy Bypass -File .\scripts\run_t24_unit_ci.ps1
```

## Runbooks And Evidence

```text
Production runbook: docs/production_runbook_latest_v1.md
Backend stack setup: docs/backend_stack_setup_latest_v1.md
Task validation matrix: local-ai-agent-system-latest-source/docs/task_validation_matrix_latest_v1.md
Project status: local-ai-agent-system-latest-source/docs/project_status_latest_v1.md
Validation reports: validation_reports/t04 through t28
```
