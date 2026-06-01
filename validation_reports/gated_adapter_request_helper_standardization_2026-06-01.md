# Gated Adapter Request Helper Standardization

Date: 2026-06-01

## Scope

Extended `tests/gated_adapter_helpers.py` so ComfyUI, GitHub, and Publishing
adapter tests share adapter request construction as well as envelope defaults.

The helper now owns the standard ComfyUI prompt/workflow, GitHub API path and
payload, Publishing payload, and request builders for the three gated adapter
request models. Adapter tests guard against reintroducing direct request-model
construction or local GitHub request wrapper functions.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check tests\gated_adapter_helpers.py tests\test_comfyui_adapter.py tests\test_github_adapter.py tests\test_publishing_adapter.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_comfyui_adapter.py tests\test_github_adapter.py tests\test_publishing_adapter.py -q -p no:cacheprovider
54 passed
```

## Alignment Result

ComfyUI, GitHub, and Publishing adapter tests now share one test boundary for
adapter request IDs, targets, operation defaults, payload defaults, request
construction, and approved/unapproved envelope setup.
