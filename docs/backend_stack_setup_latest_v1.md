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
  default ports: 6333, 6334
  local override: QDRANT_HTTP_PORT and QDRANT_GRPC_PORT in ignored .env
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

When another local stack already owns the default Qdrant host ports, keep the
container ports unchanged and override only the published host ports:

```env
QDRANT_HTTP_PORT=6335
QDRANT_GRPC_PORT=6336
QDRANT_URL=http://localhost:6335
```

`docker-compose.yml` defaults remain `6333` and `6334` when no local `.env`
override is present.

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

2026-06-02:
- full pytest: 567 passed, 1 warning
- full ruff: all checks passed
- qdrant override: docker compose config renders host ports 6335 and 6336 from local .env; ai-artist-qdrant-1 is healthy and http://localhost:6335/healthz returns healthz check passed
```

## Current Boundary

This document records the first runnable backend stack slice. The current
project has advanced beyond foundation-only status: all 28 tracker tasks are
complete, the latest final validation is 567 passed with 1 warning, and the
Safety Service, execution-envelope checks, adapter gates, helper standards, and
validation tests are implemented.

Production external writes, real social API calls, and live ComfyUI generation
remain intentionally blocked unless the required runtime configuration,
execution-envelope approval, and human approval rules are satisfied.

The reviewed next-phase optimization plan does not reopen this foundation
slice. It starts with NP01 composition root and NP02 adapter connection/client
factory, then proceeds through injectable app state, repository/storage
protocols, clock/id providers, gated-adapter protocol unification,
source-text test cleanup, and registry-driven docs validation.

NP01-NP04 next-phase optimization work is integrated with a composition root,
adapter factory, `create_app(composition_root=...)` audit repository hook,
injectable/resettable FastAPI app state, and request-time audit composition
lookup. NP04 adds production-selectable audit persistence:
`AUDIT_REPOSITORY=memory` keeps isolated local/test behavior, while
`AUDIT_REPOSITORY=postgres` routes Safety Service audit writes and reads
through the PostgreSQL `audit_event` table via `backend/audit_storage.py`.
Current non-Docker validation is 565 passed, 12 skipped, 1 warning, and ruff
clean.

2026-06-02 Qdrant port conflict review: `ai-artist-qdrant-1` starts healthy on
host ports 6335 and 6336 when another local Qdrant service owns 6333 and 6334.
The local `.env` is ignored by Git and sets `QDRANT_URL=http://localhost:6335`.
