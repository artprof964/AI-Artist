# T17 ComfyUI Adapter Validation - 2026-05-31

## Result

```text
Status: Bestanden
Task: T17 - ComfyUI adapter behind execution gate
Independent validation refreshed: 2026-05-31
```

## Scope

Implemented a local ComfyUI adapter boundary that refuses image generation
unless a supplied execution envelope is valid, allowed, signed, non-expired,
and scoped to `image_generate`.

The ComfyUI client is mocked in tests. No real ComfyUI, network, API, GPU,
storage, or provenance persistence path is invoked.

## Validation Evidence

```text
.\.venv\Scripts\python.exe -m pytest tests\test_comfyui_adapter.py -q -p no:cacheprovider
8 passed in 0.12s

.\.venv\Scripts\python.exe -m ruff check backend\comfyui_adapter.py tests\test_comfyui_adapter.py
All checks passed!

.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
96 passed, 1 skipped, 1 warning in 47.80s

.\.venv\Scripts\python.exe -m ruff check .
All checks passed!
```

The focused adapter test covers:

- missing execution envelope rejected
- malformed execution envelope payload rejected as an execution-gate error
- invalid execution envelope rejected
- disallowed execution envelope rejected
- wrong operation rejected
- expired execution envelope rejected
- missing signature rejected
- approved `image_generate` envelope succeeds with a mocked ComfyUI client

## Changed Runtime Surface

- `backend/comfyui_adapter.py`
  - adds `ComfyUIAdapter`
  - validates or rejects supplied envelope payloads before client execution
  - returns only minimal mocked generation response fields required for T17

- `tests/test_comfyui_adapter.py`
  - proves the execution gate blocks unsafe image generation attempts
  - proves the mocked approved envelope path calls the mocked client once

## Deferred

T18 image provenance storage is outside this T17 validation slice.
