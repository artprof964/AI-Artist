# T11 SubAgentOutput Schema Validation

## Scope

Implemented schema validation for `SubAgentOutput` in `backend/schemas.py`.
This task did not implement mock sub-agent orchestration or any T12+ runtime
behavior.

## Contract

`SubAgentOutput` validates the interface shape from
`local-ai-agent-system-latest-source/docs/interface_process_standard_latest_v1.md`:

- `task_id`
- `agent_name`
- `status`: `ok`, `needs_retry`, `blocked`, or `failed`
- `summary`
- `artifacts`
- `sources`
- `policy_notes`
- `confidence`: `0.0` through `1.0`
- `errors`

Artifacts, sources, and errors are structured nested models. Artifact and source
records allow extra fields for future agent-specific metadata while preserving
required validation boundaries. Errors require `code` and `message` so plain
unstructured error strings are rejected.

## Validation

Focused schema test:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_subagent_output_schema.py -p no:cacheprovider
7 passed in 0.11s
```

Full test suite:

```text
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
38 passed, 1 skipped, 1 warning in 42.29s
```

Lint:

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!
```

## Acceptance Criteria

- Valid agent outputs are accepted.
- Missing `status` is rejected.
- Malformed artifacts are rejected.
- Confidence values outside `0.0..1.0` are rejected.
- Unstructured error strings are rejected.

## Result

T11 passed on 2026-05-31.
