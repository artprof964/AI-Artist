# Gated Adapter Envelope Helper Standardization

Date: 2026-06-01

## Scope

Centralized adapter-specific execution-envelope test setup for ComfyUI,
GitHub, and Publishing adapter tests in `tests/gated_adapter_helpers.py`.

The new helper owns the stable request IDs, adapter targets, default operation
values, and approved/unapproved envelope construction for gated adapter test
paths. The adapter test modules now depend on this helper instead of defining
local approved/unapproved envelope wrappers.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check tests\gated_adapter_helpers.py tests\test_comfyui_adapter.py tests\test_github_adapter.py tests\test_publishing_adapter.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_comfyui_adapter.py tests\test_github_adapter.py tests\test_publishing_adapter.py -q -p no:cacheprovider
54 passed
```

## Alignment Result

ComfyUI, GitHub, and Publishing adapter tests now share the same
adapter-envelope fixture boundary and guard against reintroducing local
`approved_envelope` / `unapproved_*_envelope` wrappers or direct low-level
execution-envelope helper calls in adapter test modules.
