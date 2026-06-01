# OpenClaw Hook Helper Standardization

## Scope

Added `tests/openclaw_hook_helpers.py` as the shared setup boundary for
OpenClaw safety-hook integration tests.

The helper owns:

- recording Safety Service client setup
- recording adapter setup
- mock orchestration adapter setup
- OpenClaw hook event labels

`tests/test_openclaw_safety_hook.py` now imports those helpers and includes a
guard test that prevents local recording adapter classes from returning.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check tests\openclaw_hook_helpers.py tests\test_openclaw_safety_hook.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_openclaw_safety_hook.py -q -p no:cacheprovider
7 passed, 1 warning
```

