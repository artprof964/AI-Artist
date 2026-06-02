# NP03 App-State Slice Progress - 2026-06-02

## Scope

NP03 extends the NP01/NP02 composition foundation with explicit FastAPI
app-state injection and reset support. This is next-phase optimization work; it
does not reopen the completed T01-T28 tracker scope.

Related service closeout: the local Qdrant port conflict was resolved by
parameterizing `docker-compose.yml` host ports and using an ignored local `.env`
to run `ai-artist-qdrant-1` on host ports 6335 and 6336 while container ports
remain 6333 and 6334.

## Implementation

- Added `AppStateDependencies` and `app_state_dependencies(...)` to
  `backend/composition.py`.
- Added `configure_app_state(...)`, `app_composition_root(...)`, and
  `reset_app_composition_root(...)` to `backend/app.py`.
- Updated audit endpoints to resolve the current composition root from
  request-time app state instead of closing over the initially supplied root.
- Added focused tests proving app-level audit repository isolation, app-state
  reset without route rebuilding, and reset isolation between app instances.
- Updated shared Safety Service test helpers so audit endpoint tests clear the
  app-state repository actually used by the shared `TestClient`.
- Added a tree-shape guard that keeps Qdrant host ports locally overridable via
  `QDRANT_HTTP_PORT` and `QDRANT_GRPC_PORT`.

## Validation Results

Focused regression set:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_composition.py tests\test_audit_event_log.py tests\test_tree_shape.py tests\test_safety_service_endpoints.py tests\test_production_readiness.py tests\test_connection_settings.py -q -p no:cacheprovider
```

Result:

```text
61 passed, 1 warning in 1.36s
```

Focused ruff:

```powershell
.\.venv\Scripts\python.exe -m ruff check backend\app.py backend\composition.py tests\test_composition.py tests\test_audit_event_log.py tests\test_tree_shape.py tests\safety_service_client_helpers.py
```

Result:

```text
All checks passed!
```

Full pytest:

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result:

```text
567 passed, 1 warning in 29.41s
```

Full ruff:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Result:

```text
All checks passed!
```

Qdrant runtime verification:

```powershell
docker compose ps --all
docker compose config qdrant
curl.exe -fsS http://localhost:6335/healthz
```

Result:

```text
ai-artist-qdrant-1 is healthy.
Rendered compose publishes host 6335 -> container 6333 and host 6336 -> container 6334.
healthz check passed.
```

## Residual Follow-Up

- Canonicalize, classify, policy, and execution-envelope routes still call the
  existing module-level service functions. The NP03 slice intentionally wires
  audit routes first and keeps remaining direct global hook points documented in
  `tests/test_composition.py`.
- `backend.app` imports the composition root, which imports the adapter factory.
  The current environment includes those dependencies; a future production
  packaging pass may choose to lazy-load adapter factories if a slimmer Safety
  Service import surface is required.

## Status

NP03 is integrated and validated as a next-phase optimization slice. T01-T28
remain complete with 0 open implementation tasks.
