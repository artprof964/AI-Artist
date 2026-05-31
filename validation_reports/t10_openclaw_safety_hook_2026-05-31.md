# T10 OpenClaw Safety Hook Validation

Date: 2026-05-31

## Scope

Validated the OpenClaw safety-service tool hook:

> Integration test attempts a tool call and confirms Safety Service receives the
> pre-execution request before any adapter runs.

## Results

```text
.venv\Scripts\python.exe -m pytest tests\test_openclaw_safety_hook.py -q -p no:cacheprovider
2 passed, 1 warning in 0.24s

.venv\Scripts\python.exe -m ruff check backend\openclaw_hook.py tests\test_openclaw_safety_hook.py
All checks passed!

.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
28 passed, 1 skipped, 1 warning in 42.63s

.venv\Scripts\python.exe -m ruff check .
All checks passed!
```

## Notes

- `execute_tool_call_with_safety` builds a `PolicyEvaluateRequest` and sends it
  to the Safety Service client before adapter execution.
- The Safety Service request preserves request id, operation, request kind,
  requester scope, policy scope, source freshness, correlation id, tool name,
  and non-secret tool metadata.
- Secret-shaped metadata and tool argument keys are redacted before the Safety
  Service receives the policy request; approved adapters still receive the
  original `ToolCallRequest`.
- Allowed read-only tool calls run adapters only after the Safety Service
  policy decision.
- Denied publish tool calls do not run adapters.
- The warning is the existing FastAPI/Starlette TestClient deprecation warning.

## Residual Risk

- Secret redaction is currently key-name based via `SECRET_KEY_TERMS`. T10 test
  coverage proves that secret-shaped keys such as `api_key`, `oauth_token`, and
  `authorization` are not sent to the Safety Service, but arbitrary secret
  values under unrecognized keys would not be detected by this hook.
