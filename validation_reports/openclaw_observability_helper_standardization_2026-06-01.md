# OpenClaw Observability Helper Standardization

## Scope

Migrated `tests/test_observability.py` from local OpenClaw safety and
orchestration test doubles to `tests/openclaw_hook_helpers.py`.

The observability integration path now shares the same recording Safety Service
client and mock orchestration adapter as the OpenClaw safety-hook tests, and a
guard test prevents local `LocalSafetyClient` or `LocalOrchestrationAdapter`
classes from returning.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check tests\test_observability.py tests\openclaw_hook_helpers.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_observability.py tests\test_openclaw_safety_hook.py -q -p no:cacheprovider
12 passed, 1 warning
```

