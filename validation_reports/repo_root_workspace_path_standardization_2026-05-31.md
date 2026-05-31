# Repo Root And Workspace Path Standardization Validation - 2026-05-31

## Scope

Extended the repository path contract to cover test repo-root resolution and
workspace file path/text reads.

## Changes

- Added `WORKSPACES_DIR`, `workspace_path`, and `read_workspace_text` to
  `backend/repo_paths.py`.
- Updated tests that computed `Path(__file__).resolve().parents[1]` directly to
  use `repo_root_from`.
- Updated workspace and rubric validators to read workspace files through the
  shared workspace path/text helpers.
- Added a repo path guard test that fails if tests reintroduce direct
  `Path(__file__).resolve().parents[1]` repo-root calculation.

## Validation

```text
pytest tests/test_repo_paths.py tests/test_openclaw_workspace.py tests/test_critic_curator.py tests/test_postgres_migrations.py -q -p no:cacheprovider
17 passed in 3.76s

ruff check backend/repo_paths.py tests
All checks passed.
```

## Result

Passed. Test repo-root lookup and workspace file reads now flow through
`backend/repo_paths.py`.
