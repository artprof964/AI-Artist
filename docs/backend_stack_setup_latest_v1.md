# Backend Stack Setup - Latest

## Purpose

This document records the first runnable backend stack slice for AI-Artist.
It supports T03 and T04 from the project tracker: repository scaffold and
Docker Compose foundation. The FastAPI Safety Service endpoints for T05 are
also present and covered by local API tests.

## Services

```text
PostgreSQL 16
  port: 5432
  database: ai_artist
  user: ai_artist
  purpose: request runs, source registry, cache metadata, audit events

Redis 7
  port: 6379
  purpose: queue state, locks, rate-limit counters, transient job state

Qdrant
  ports: 6333, 6334
  purpose: vector retrieval for the Knowledge Agent

MinIO
  ports: 9000, 9001
  purpose: generated images, source snapshots, response artifacts

OPA
  port: 8181
  policy path: policies/opa/ai_artist.rego
  purpose: default-deny policy authority for reuse and privileged execution
```

## Local Commands

```powershell
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.\\.venv\\Scripts\\python.exe -m pytest
.\\.venv\\Scripts\\python.exe -m ruff check .
docker compose config
docker compose up -d postgres redis qdrant minio opa
docker compose ps
docker compose down
```

## Scaffolded Paths

```text
docker-compose.yml
infra/postgres/init/001_query_tracking.sql
policies/opa/ai_artist.rego
workspaces/ai-artist-main/
workspaces/social-scout/
workspaces/image-gen/
workspaces/critic-curator/
```

## Backend Safety Service

```text
backend/app.py
  GET  /health
  POST /v1/requests/canonicalize
  POST /v1/requests/classify
  POST /v1/policy/evaluate
  POST /v1/execution/envelope
  POST /v1/audit/events

backend/schemas.py
  RequestEnvelope-adjacent canonicalize/classify/policy schemas
  execution-envelope and audit-event schemas

backend/service.py
  stable fingerprinting
  simple read/action/mixed classification
  local default-deny scaffold policy for sensitive operations
  local HMAC execution-envelope signing
  secret-key redaction for audit payloads
```

## Validation Evidence

```text
2026-05-31:
- docker compose config: passed
- docker compose up -d postgres redis qdrant minio opa: passed
- service health: docker compose ps reports all five services healthy; PostgreSQL accepting connections; Redis PONG; Qdrant healthz passed; MinIO live 200; OPA health 200
- pytest: 10 passed, 2 warnings
- ruff: all checks passed
```

## Current Boundary

The stack is intentionally foundation-only. Real social API calls, publishing,
and live ComfyUI generation remain blocked until the Safety Service,
execution-envelope checks, and validation tests are implemented.
