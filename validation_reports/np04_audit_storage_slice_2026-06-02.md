# NP04 Audit Storage Slice - 2026-06-02

## Scope

NP04 repository/storage protocols focused on the highest-value target:
production-backed audit persistence.

## Implemented

- Added `backend/audit_storage.py`.
- Added `PostgresAuditEventRepository` implementing the existing
  `AuditEventRepository` protocol.
- Added `AUDIT_REPOSITORY=memory|postgres` connection setting.
- Wired `CompositionRoot` to use Postgres audit storage when
  `AUDIT_REPOSITORY=postgres`; default remains isolated in-memory storage.
- Added `psycopg[binary]` as a production dependency in `pyproject.toml` and
  `requirements.txt`.
- Updated `.env.example` and production runbook with the audit repository
  selector.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_audit_storage.py tests\test_connection_settings.py tests\test_composition.py tests\test_production_readiness.py -q -p no:cacheprovider
```

Result: 48 passed, 1 warning.

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --ignore=tests/test_postgres_migrations.py
```

Result: 565 passed, 12 skipped, 1 warning.

```powershell
.\.venv\Scripts\ruff.exe check .
```

Result: All checks passed.

## Blocked Live Check

The full pytest command reached the existing Docker-backed PostgreSQL migration
test and failed because Docker Desktop was not reachable from this shell:

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine
```

The same Docker limitation blocked a live Postgres insert/list proof for
`AUDIT_REPOSITORY=postgres`. Unit tests validate SQL shape, row hydration,
repository selection, and composition wiring without requiring Docker.
