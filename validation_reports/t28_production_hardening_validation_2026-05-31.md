# T28 Production Hardening Validation - 2026-05-31

## Scope

Implemented deterministic local production readiness support for T28 in:

- `backend/readiness.py`
- `tests/test_production_readiness.py`
- `docs/production_runbook_latest_v1.md`
- `validation_reports/t28_production_hardening_validation_2026-05-31.md`

The readiness support is local-only and does not make network calls during tests.

## Coverage

- Verifies required runbook sections exist for startup, environment validation,
  health checks, backups, restore checks, retention policy, incident contacts,
  and validation evidence.
- Validates `.env.example` against an explicit required environment schema while
  allowing secret values to remain blank.
- Defines local stack and Safety Service health check commands.
- Defines PostgreSQL, MinIO, and Qdrant backup command entries.
- Defines PostgreSQL, MinIO, and Qdrant restore-check command entries.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_production_readiness.py -q -p no:cacheprovider
```

Result:

```text
5 passed in 0.02s
```

```powershell
.\.venv\Scripts\python.exe -m ruff check backend/readiness.py tests/test_production_readiness.py
```

Result:

```text
All checks passed!
```

## Status

T28 acceptance criteria are satisfied for deterministic local production
readiness coverage.
