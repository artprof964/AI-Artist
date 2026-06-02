# Production Runbook - Latest

## Purpose

This runbook records deterministic local production readiness for AI-Artist.
It is production readiness for the local stack: all checks are practical,
repeatable, and avoid calls to external services.

## Ownership And Scope

The Safety Service owns request canonicalization, classification, local policy
evaluation, audit recording, and execution-envelope generation. The local stack
contains PostgreSQL, Redis, Qdrant, MinIO, and OPA through `docker compose`.
Checked-in readiness command definitions are built through shared shell command
helpers before they are mirrored into this runbook.
Backup paths and local object-store aliases are centralized in the readiness
path contract before command definitions or runbook examples are changed.

Primary operator: local AI-Artist maintainer.
Escalation owner: repository owner or current implementation lead.

## Startup And Shutdown

Start the backing services:

```powershell
docker compose up -d postgres redis qdrant minio opa
docker compose ps
```

If another local stack already owns Qdrant host ports `6333` and `6334`, set
the ignored local `.env` before startup:

```env
QDRANT_HTTP_PORT=6335
QDRANT_GRPC_PORT=6336
QDRANT_URL=http://localhost:6335
```

This changes only the published host ports. The Qdrant container still listens
on its standard internal ports, so Compose health checks continue to use the
container-local `6333`.

Start the Safety Service:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Or start it through the project CLI:

```powershell
.\.venv\Scripts\python.exe -m backend.cli serve --host 127.0.0.1 --port 8000
```

Stop the local stack:

```powershell
docker compose down
```

## Environment Validation

Use `.env.example` as the required environment schema. The file is validated
against the shared connection settings registry rendering and must document all
required keys without requiring real secrets in source control.

Required secret keys may be blank in `.env.example`:

```text
deepseek-open-art
SLACK_BOT_TOKEN
git_ai-artist_codex_token
```

`deepseek-open-art` is the project-standard LLM API key name. The loader keeps
`DEEPSEEK_API_KEY` only as a backward-compatible alias, and new setup,
readiness, smoke-test, and deployment instructions must use `deepseek-open-art`.

PowerShell setup example:

```powershell
${env:deepseek-open-art}="..."
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
SAFETY_SERVICE_URL
AUDIT_REPOSITORY
```

`AUDIT_REPOSITORY` defaults to `memory` for isolated local development and
tests. Set it to `postgres` before Safety Service startup when audit events
must be persisted in the production-backed `audit_event` table:

```powershell
$env:AUDIT_REPOSITORY="postgres"
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

When a local Qdrant port override is active, run the Qdrant health check
against the configured `QDRANT_URL` host port instead of `localhost:6333`.

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
curl.exe -fsS -X POST $env:QDRANT_URL/collections/{collection}/snapshots
```

Record each generated snapshot name under `.codex_tmp/backups/qdrant/`.
When no Qdrant override is active, set `$env:QDRANT_URL="http://localhost:6333"`
or use `http://localhost:6333` directly.

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
curl.exe -fsS $env:QDRANT_URL/collections/{collection}/snapshots
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

2026-06-02 local Qdrant override and app-state regression evidence:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_tree_shape.py tests\test_composition.py tests\test_audit_event_log.py -q -p no:cacheprovider
docker compose config qdrant
docker compose ps --all
curl.exe -fsS http://localhost:6335/healthz
```

Result: Qdrant compose host-port overrides are covered by tests, rendered
configuration publishes 6335 and 6336 to container ports 6333 and 6334,
`ai-artist-qdrant-1` reports healthy, and the local override health endpoint
returns `healthz check passed`.

2026-06-02 production CLI wrap-up evidence:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_cli.py -q -p no:cacheprovider
.\.venv\Scripts\ruff.exe check backend\cli.py tests\test_cli.py pyproject.toml
.\.venv\Scripts\python.exe -m backend.cli health
.\.venv\Scripts\python.exe -m backend.cli classify "Generate an image from this prompt"
.\.venv\Scripts\python.exe -m backend.cli policy --request-kind read --operation read --no-requires-human-approval
.\.venv\Scripts\python.exe -m backend.cli envelope "Publish this update" --operation publish --target slack://workspace/channel
.\.venv\Scripts\python.exe -m backend.cli envelope "Publish this update" --operation publish --target slack://workspace/channel --approved --approver-scope user:owner
.\.venv\Scripts\python.exe -m backend.cli serve --host 127.0.0.1 --port 8766
curl.exe -fsS http://127.0.0.1:8766/health
```

Result: focused CLI tests passed, ruff passed, direct CLI examples returned the
expected JSON decisions, and a CLI-launched live service returned healthy on
port 8766. Exact examples are in `docs/cli_manual_latest_v1.md`.
