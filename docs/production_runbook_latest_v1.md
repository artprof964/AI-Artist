# Production Runbook - Latest

## Purpose

This runbook records deterministic local production readiness for AI-Artist.
It is production readiness for the local stack: all checks are practical,
repeatable, and avoid calls to external services.

## Ownership And Scope

The Safety Service owns request canonicalization, classification, local policy
evaluation, audit recording, and execution-envelope generation. The local stack
contains PostgreSQL, Redis, Qdrant, MinIO, and OPA through `docker compose`.

Primary operator: local AI-Artist maintainer.
Escalation owner: repository owner or current implementation lead.

## Startup And Shutdown

Start the backing services:

```powershell
docker compose up -d postgres redis qdrant minio opa
docker compose ps
```

Start the Safety Service:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Stop the local stack:

```powershell
docker compose down
```

## Environment Validation

Use `.env.example` as the required environment schema. The file must document
all required keys without requiring real secrets in source control.

Required secret keys may be blank in `.env.example`:

```text
LLM_API_KEY
SLACK_BOT_TOKEN
git_ai-artist_codex_token
```

Required local service keys:

```text
LLM_API_URL
LLM_PRIMARY_MODEL
LLM_FALLBACK_MODEL
LLM_CLASSIFIER_MODEL
LLM_EMBEDDING_MODEL
OPENCLAW_WORKSPACE_ROOT
OPENCLAW_GATEWAY_URL
DATABASE_URL
QDRANT_URL
MINIO_ENDPOINT
REDIS_URL
OPA_URL
COMFYUI_URL
```

Local validation command:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_production_readiness.py -q -p no:cacheprovider
```

## Health Checks

Local stack health checks:

```powershell
docker compose ps
docker compose exec -T postgres pg_isready -U ai_artist -d ai_artist
docker compose exec -T redis redis-cli ping
curl.exe -fsS http://localhost:6333/healthz
curl.exe -fsS http://localhost:9000/minio/health/live
curl.exe -fsS http://localhost:8181/health
```

Expected local stack signals:

```text
PostgreSQL accepts connections.
Redis returns PONG.
Qdrant returns healthz check passed.
MinIO live endpoint returns a non-error response.
OPA health endpoint returns a non-error response.
```

Safety Service health check:

```powershell
curl.exe -fsS http://localhost:8000/health
```

Expected Safety Service signal:

```json
{"status":"ok","service":"ai-artist-safety-service"}
```

## Backup Commands

Create the local backup folder:

```powershell
New-Item -ItemType Directory -Force .codex_tmp\backups\postgres
New-Item -ItemType Directory -Force .codex_tmp\backups\minio
New-Item -ItemType Directory -Force .codex_tmp\backups\qdrant
```

PostgreSQL backup:

```powershell
docker compose exec -T postgres pg_dump -U ai_artist -d ai_artist --format=custom --file=/tmp/ai_artist_latest.dump
docker compose cp postgres:/tmp/ai_artist_latest.dump .codex_tmp/backups/postgres/
```

MinIO backup:

```powershell
mc mirror --overwrite local-ai-artist/ .codex_tmp/backups/minio/
```

Qdrant backup:

```powershell
curl.exe -fsS -X POST http://localhost:6333/collections/{collection}/snapshots
```

Record each generated snapshot name under `.codex_tmp/backups/qdrant/`.

## Restore Check Commands

These commands are restore checks only. They verify that backup artifacts are
readable before any destructive restore procedure is attempted.

PostgreSQL restore check:

```powershell
docker compose exec -T postgres pg_restore --list /tmp/ai_artist_latest.dump
```

MinIO restore check:

```powershell
mc ls --recursive .codex_tmp/backups/minio/
```

Qdrant restore check:

```powershell
curl.exe -fsS http://localhost:6333/collections/{collection}/snapshots
```

The restore check passes when the PostgreSQL dump lists contents, MinIO backup
objects are visible, and Qdrant lists the snapshot created during backup.

## Retention Policy

Retain local backups for 14 days in `.codex_tmp/backups/`. Retain the newest
known-good PostgreSQL dump, MinIO mirror, and Qdrant snapshot even if it is
older than 14 days. Delete only local backup artifacts after confirming the
newest restore check has passed.

## Incident Contacts

Primary contact: local AI-Artist maintainer.
Secondary contact: repository owner or current implementation lead.

Escalate immediately when health checks fail after restart, restore checks fail,
secrets appear in logs or committed files, or policy evaluation allows a
sensitive operation without the expected approval envelope.

## Validation Evidence

T28 readiness is validated with:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_production_readiness.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend/readiness.py tests/test_production_readiness.py
```
