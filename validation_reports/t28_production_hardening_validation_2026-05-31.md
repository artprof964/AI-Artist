# T28 Production Hardening Validation - 2026-06-01 Refresh

## Scope

T28 implements deterministic local production readiness support in:

- `backend/readiness.py`
- `backend/readiness_paths.py`
- `backend/connection_settings.py`
- `backend/shell_commands.py`
- `backend/repo_paths.py`
- `backend/health_contracts.py`
- `backend/markdown_utils.py`
- `tests/test_production_readiness.py`
- `docs/production_runbook_latest_v1.md`
- `docs/final_stack_specs_latest_v1.md`

The readiness support is local-only and does not make network calls during
tests.

## Coverage

- Verifies required runbook sections exist for startup/shutdown, environment
  validation, health checks, backups, restore checks, retention policy,
  incident contacts, and validation evidence.
- Validates `.env.example` through the shared connection settings registry,
  allowing secret values to remain blank and rejecting real secret-looking
  placeholders.
- Defines local stack and Safety Service health check command entries.
- Defines PostgreSQL, MinIO, and Qdrant backup command entries.
- Defines PostgreSQL, MinIO, and Qdrant restore-check command entries.
- Verifies command construction uses shared shell-command helpers.
- Verifies backup paths, container dump path, MinIO source alias, repository
  paths, health expected signals, and Markdown heading parsing are centralized.
- Verifies final stack/spec documentation exists at
  `docs/final_stack_specs_latest_v1.md`.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_production_readiness.py -q -p no:cacheprovider
```

Result:

```text
13 passed in 0.04s
```

```powershell
.\.venv\Scripts\python.exe -m ruff check backend\security_review.py backend\security_review_contracts.py tests\test_security_review.py backend\readiness.py backend\readiness_paths.py tests\test_production_readiness.py
```

Result:

```text
All checks passed!
```

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result:

```text
553 passed, 1 warning in 27.95s
```

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Result:

```text
All checks passed!
```

## Status

T28 acceptance criteria are satisfied for deterministic local production
readiness coverage. The warning in the full suite is the existing
FastAPI/Starlette `TestClient` deprecation warning.
