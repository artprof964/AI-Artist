# Gated Adapter Client Helper Standardization

Date: 2026-06-01

## Scope

Extended `tests/gated_adapter_helpers.py` so ComfyUI, GitHub, Publishing
adapter tests, and Publishing Agent audit tests share their deterministic fake
client doubles.

The helper now owns mocked ComfyUI workflow submission, mocked GitHub API write
responses, mocked publishing responses, and the secret-echo publishing client
used to verify audit redaction. Adapter tests guard against reintroducing local
mock client classes.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check tests\gated_adapter_helpers.py tests\test_comfyui_adapter.py tests\test_github_adapter.py tests\test_publishing_adapter.py tests\test_publishing_agent.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_comfyui_adapter.py tests\test_github_adapter.py tests\test_publishing_adapter.py tests\test_publishing_agent.py -q -p no:cacheprovider
59 passed
```

## Alignment Result

Gated adapter test setup now centralizes adapter request IDs, targets,
operation defaults, payload defaults, request construction, approved/unapproved
envelope setup, mocked client calls, mocked client responses, and
secret-redaction client echoes.
