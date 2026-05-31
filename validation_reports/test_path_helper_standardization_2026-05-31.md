# Test Path Helper Standardization Validation - 2026-05-31

## Scope

Centralized repo-wide test source inspection helpers used by guard tests.

## Changes

- Added `tests/path_helpers.py` for shared project-root resolution, backend
  source reads, test source reads, and test-module source iteration.
- Replaced repeated guard-test loops in connection settings, canonical hashing,
  time utilities, shell commands, and repo path tests with the shared helper.
- Added guard coverage that prevents repo-wide test source scans from
  reintroducing local `glob("test_*.py")` or `Path("tests") / ...` loops.

## Validation

```text
pytest tests/test_repo_paths.py tests/test_shell_commands.py tests/test_connection_settings.py tests/test_canonical_hash.py tests/test_time_utils.py -q -p no:cacheprovider
46 passed in 0.40s

ruff check tests/path_helpers.py tests/test_repo_paths.py tests/test_shell_commands.py tests/test_connection_settings.py tests/test_canonical_hash.py tests/test_time_utils.py
All checks passed.

ruff check .
All checks passed.

pytest -p no:cacheprovider
411 passed, 1 skipped, 1 warning in 22.84s

git diff --check
No whitespace errors; CRLF normalization warnings only.
```

## Result

Passed focused validation. Repo-wide guard tests now share test path and source
inspection helpers.
