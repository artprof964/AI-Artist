# Gated Adapter Harness Standardization Validation - 2026-06-01

## Scope

- Added `ComfyUIAdapterHarness`, `comfyui_adapter_harness_for_test()`, `PublishingAdapterHarness`, and `publishing_adapter_harness_for_test()` to `tests/gated_adapter_helpers.py`.
- Migrated ComfyUI and Publishing adapter tests to shared adapter/client setup.
- Added guards that prevent `tests/test_comfyui_adapter.py` and `tests/test_publishing_adapter.py` from constructing adapters directly.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check tests\gated_adapter_helpers.py tests\test_comfyui_adapter.py tests\test_publishing_adapter.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_comfyui_adapter.py tests\test_publishing_adapter.py tests\test_github_adapter.py tests\test_adapter_results.py -q -p no:cacheprovider
58 passed
```
