# Publishing Agent Helper Standardization - 2026-06-01

## Scope

Extended `tests/gated_adapter_helpers.py` so Publishing Agent tests share the
same publishing target, payload, approved/unapproved envelope defaults,
deterministic local publisher client, secret-echo publisher client, agent
harnesses, and `PublishingAgentRequest` construction used by adjacent publishing
adapter coverage.

`tests/test_publishing_agent.py` now guards against direct
`PublishingAgent`, `LocalPublishingClient`, and `PublishingAgentRequest` imports
and against reintroducing local publishing envelope builders.

The project-standard LLM API key remains `deepseek-open-art`; `DEEPSEEK_API_KEY`
is compatibility-only through the connection settings registry.

## Validation

```powershell
.\.venv\Scripts\python.exe -m ruff check tests\gated_adapter_helpers.py tests\test_publishing_agent.py tests\test_publishing_adapter.py
```

Result: all checks passed.

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_publishing_agent.py tests\test_publishing_adapter.py tests\test_github_adapter.py tests\test_comfyui_adapter.py -q -p no:cacheprovider
```

Result: 60 passed.

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_publishing_agent.py tests\test_publishing_adapter.py tests\test_github_adapter.py tests\test_comfyui_adapter.py tests\test_policy_contracts.py -q -p no:cacheprovider
```

Result: 69 passed.

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result: 550 passed, 1 warning.
