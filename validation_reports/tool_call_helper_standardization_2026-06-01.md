# Tool Call Helper Standardization - 2026-06-01

## Scope

OpenClaw hook and observability tests now share `tests/tool_call_helpers.py`
for standard `ToolCallRequest` construction. This keeps tool-call defaults,
request scope, correlation IDs, request IDs, arguments, metadata, and source
freshness setup in one test boundary.

## Implementation

- Added `tool_call_request_for_test(...)` with overridable defaults for tool
  name, operation, request kind, requester scope, policy scope, arguments,
  metadata, correlation ID, request ID, and source freshness.
- Migrated direct `ToolCallRequest(...)` setup in OpenClaw safety hook and
  observability tests to the shared helper.
- Added guard tests that keep those modules from reintroducing local
  `ToolCallRequest` constructor setup.

## Validation

Focused validation passed:

```powershell
.\.venv\Scripts\python.exe -m ruff check tests\tool_call_helpers.py tests\test_openclaw_safety_hook.py tests\test_observability.py
.\.venv\Scripts\python.exe -m pytest tests\test_openclaw_safety_hook.py tests\test_observability.py -q -p no:cacheprovider
```

Result: 10 passed, 1 known Starlette TestClient warning.
