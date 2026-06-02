# Production Startup Validation - 2026-06-02

Scope: production readiness, service startup paths, and final process validation requirements.

## Findings

1. Qdrant override coverage was incomplete for backup and restore commands.
   `docker-compose.yml` supports `QDRANT_HTTP_PORT` and `QDRANT_GRPC_PORT`, and the runbook documents `QDRANT_URL=http://localhost:6335` for local port conflicts. The health-check section says to use the configured `QDRANT_URL`, but the Qdrant backup and restore examples still hard-code `http://localhost:6333`. `backend/readiness.py` also builds Qdrant health, backup, and restore command definitions from `DEFAULT_QDRANT_URL`, while `tests/test_production_readiness.py` asserts that default URL. In an override run, `docker compose config` currently renders Qdrant on host ports `6335/6336`, so the runbook backup and restore examples targeting `6333` can fail or hit the wrong local stack.

   Follow-up completed in the production wrap-up: `docs/production_runbook_latest_v1.md`
   and `docs/cli_manual_latest_v1.md` now show `$env:QDRANT_URL` for Qdrant
   host-side snapshot commands and document the default `localhost:6333` fallback.

2. Audit persistence has a production-backed option after NP04.
   `AUDIT_REPOSITORY=postgres` now routes Safety Service audit writes and reads through `backend/audit_storage.py` and the PostgreSQL `audit_event` table. The default remains `memory` for isolated local development and tests. Live Postgres proof is still pending in this shell because Docker Desktop is not reachable.

3. Final process validation should include a live ASGI startup probe.
   Focused tests cover factory-created FastAPI apps and static readiness contracts. A live probe confirmed `backend.app:app` starts and serves `/health` plus `/v1/requests/canonicalize`, but that check is not yet captured as a required final process gate.

   Follow-up completed in the production wrap-up: `docs/production_runbook_latest_v1.md`
   now records CLI startup and live probe evidence, and `docs/cli_manual_latest_v1.md`
   includes tested live HTTP examples.

## Commands Run

```powershell
git status --short
rg --files
rg -n "(uvicorn|gunicorn|FastAPI|startup|health|ready|docker|compose|SERVICE|PORT|ENV|production|prod|runbook|pytest|ruff|mypy)" .
.\.venv\Scripts\python.exe -m pytest tests\test_production_readiness.py tests\test_composition.py tests\test_adapter_factory.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\app.py backend\composition.py backend\adapter_factory.py backend\readiness.py tests\test_production_readiness.py tests\test_composition.py tests\test_adapter_factory.py
docker compose config
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8765
curl.exe -fsS http://127.0.0.1:8765/health
Invoke-RestMethod -Uri 'http://127.0.0.1:8765/v1/requests/canonicalize' -Method Post -ContentType 'application/json' -Body '{"request_text":"  Research   Flux trends  ","requester_scope":"user:local","policy_scope":"workspace:ai-artist-main","channel":"cli"}' | ConvertTo-Json -Compress
```

## Results

- Focused pytest: 26 passed, 1 existing FastAPI/Starlette `TestClient` deprecation warning.
- Focused ruff: all checks passed.
- `docker compose config`: passed; local `.env` rendered Qdrant host ports `6335` and `6336`.
- Live `uvicorn backend.app:app` probe: `/health` returned `{"status":"ok","service":"ai-artist-safety-service"}`; `/v1/requests/canonicalize` returned a 200 response with canonical text and a SHA-256 request fingerprint.

## Recommended Final Test Sequence

```powershell
docker compose config
docker compose up -d postgres redis qdrant minio opa
docker compose ps --all
docker compose exec -T postgres pg_isready -U ai_artist -d ai_artist
docker compose exec -T redis redis-cli ping
curl.exe -fsS $env:QDRANT_URL/healthz
curl.exe -fsS http://localhost:9000/minio/health/live
curl.exe -fsS http://localhost:8181/health
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
curl.exe -fsS http://127.0.0.1:8000/health
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/v1/requests/canonicalize' -Method Post -ContentType 'application/json' -Body '{"request_text":"  Research   Flux trends  ","requester_scope":"user:local","policy_scope":"workspace:ai-artist-main","channel":"cli"}' | ConvertTo-Json -Compress
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check .
docker compose down
```

When no Qdrant override is active, set `$env:QDRANT_URL="http://localhost:6333"` before the health check or call `curl.exe -fsS http://localhost:6333/healthz` directly.
