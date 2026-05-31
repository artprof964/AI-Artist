# Connection Endpoint Readiness Standardization Validation - 2026-05-31

## Scope

Centralized service endpoint URL composition for production readiness health, backup, and restore commands so local service URLs move through the connection registry instead of readiness-only literals.

## Changes

- Added `SAFETY_SERVICE_URL` and `DEFAULT_SAFETY_SERVICE_URL` to the shared connection settings registry.
- Added `connection_endpoint_url` for slash-normalized endpoint composition.
- Updated `backend/readiness.py` to compose Qdrant, MinIO, OPA, and Safety Service command URLs from shared connection defaults.
- Updated `.env.example`, runbook, stack docs, tracker, and validation matrix for the new standard connection setting.
- Added tests proving endpoint URL composition and guarding readiness against reintroducing local service URL literals.

## Validation

```text
pytest tests/test_connection_settings.py tests/test_production_readiness.py -q -p no:cacheprovider
16 passed in 0.07s

ruff check backend/connection_settings.py backend/readiness.py tests/test_connection_settings.py tests/test_production_readiness.py
All checks passed.
```

## Result

Passed. Readiness health, backup, and restore endpoint command URLs now flow through `backend/connection_settings.py` before local service endpoints are exposed in readiness checks.
