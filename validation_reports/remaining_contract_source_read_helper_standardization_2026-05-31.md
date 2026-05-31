# Remaining Contract Source Read Helper Standardization Validation - 2026-05-31

## Scope

Expanded shared backend source-read helper usage across remaining simple
contract tests.

## Changes

- Migrated observability constants, OpenClaw safety hook, Publishing Agent,
  publishing status, Slack contracts, source ingestion contracts, and source
  freshness tests to `read_backend_source`.
- Extended repo path guard coverage so these migrated contract tests cannot
  reintroduce local `repo_root_from(Path(__file__))`, `read_backend_module_text`,
  or `read_repo_text` usage.

## Validation

```text
pytest tests/test_repo_paths.py tests/test_observability_constants.py tests/test_openclaw_safety_hook.py tests/test_publishing_agent.py tests/test_publishing_status.py tests/test_slack_contracts.py tests/test_source_ingestion_contracts.py tests/test_source_freshness.py -q -p no:cacheprovider
32 passed, 1 warning in 0.54s

ruff check tests/test_repo_paths.py tests/test_observability_constants.py tests/test_openclaw_safety_hook.py tests/test_publishing_agent.py tests/test_publishing_status.py tests/test_slack_contracts.py tests/test_source_ingestion_contracts.py tests/test_source_freshness.py
All checks passed.

ruff check .
All checks passed.

pytest -p no:cacheprovider
412 passed, 1 skipped, 1 warning in 22.62s

git diff --check
No whitespace errors; CRLF normalization warnings only.
```

## Result

Passed focused validation. Remaining simple contract tests now use shared
backend source-read helpers.
