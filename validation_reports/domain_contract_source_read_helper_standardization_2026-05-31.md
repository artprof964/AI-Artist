# Domain Contract Source Read Helper Standardization Validation - 2026-05-31

## Scope

Expanded shared backend source-read helper usage across domain contract tests.

## Changes

- Migrated image provenance, Critic/Curator, Critic rubric, Knowledge Agent,
  mock sub-agent, sub-agent output, and sub-agent status contract tests to
  `read_backend_source`.
- Kept workspace file reads on the shared project root from `tests/path_helpers.py`.
- Extended repo path guard coverage so migrated domain contract tests cannot
  reintroduce local `repo_root_from(Path(__file__))`, `read_backend_module_text`,
  or `read_repo_text` usage.

## Validation

```text
pytest tests/test_repo_paths.py tests/test_image_provenance.py tests/test_critic_curator.py tests/test_critic_rubric.py tests/test_knowledge_agent.py tests/test_mock_subagents.py tests/test_subagent_output_contracts.py tests/test_subagent_status.py -q -p no:cacheprovider
55 passed in 0.36s

ruff check tests/test_repo_paths.py tests/test_image_provenance.py tests/test_critic_curator.py tests/test_critic_rubric.py tests/test_knowledge_agent.py tests/test_mock_subagents.py tests/test_subagent_output_contracts.py tests/test_subagent_status.py
All checks passed.

ruff check .
All checks passed.

pytest -p no:cacheprovider
412 passed, 1 skipped, 1 warning in 22.80s

git diff --check
No whitespace errors; CRLF normalization warnings only.
```

## Result

Passed focused validation. Domain contract tests now use shared backend
source-read helpers.
