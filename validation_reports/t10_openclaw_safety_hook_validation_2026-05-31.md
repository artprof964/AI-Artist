# T10 OpenClaw Safety Hook Validation

Date: 2026-05-31

## Scope

Validated the OpenClaw safety-service tool hook:

> Integration test attempts a tool call and confirms Safety Service receives the
> pre-execution request before any adapter runs.

## Results

```text
.venv\Scripts\python.exe -m pytest tests\test_openclaw_safety_hook.py -q -p no:cacheprovider
2 passed, 1 warning in 0.26s

.venv\Scripts\python.exe -m ruff check backend\openclaw_hook.py tests\test_openclaw_safety_hook.py
All checks passed!

.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
28 passed, 1 skipped, 1 warning in 44.68s

.venv\Scripts\python.exe -m ruff check .
All checks passed!
```

## Notes

- `execute_tool_call_with_safety` builds a `PolicyEvaluateRequest` before adapter execution.
- Safety Service receives request id, operation, request kind, requester scope, policy scope, explicitly asserted source freshness fields, tool metadata, and correlation id.
- Safety Service metadata redacts secret-shaped keys while the adapter still receives the original request object after approval.
- Allowed read-only tool calls execute the adapter only after the Safety Service policy decision.
- Denied publish tool calls preserve the denial metadata and do not run the adapter.
- Full-suite warning is the existing FastAPI/Starlette TestClient deprecation warning.
