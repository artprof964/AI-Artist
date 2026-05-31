# T24 Unit CI Implementation - 2026-05-31

## Scope

Implemented T24 only: a deterministic unit-test CI gate for the safety service and
policy surface.

## Changed Files

- `.github/workflows/t24-safety-unit-ci.yml`
- `pyproject.toml`
- `requirements.txt`
- `scripts/run_t24_unit_ci.ps1`
- `tests/test_opa_policy.py`
- `tests/test_safety_service_units.py`
- `validation_reports/t24_unit_ci_implementation_2026-05-31.md`

## Implementation Notes

- Added `coverage[toml]` and `pytest-cov` to dev and requirements dependencies.
- Added coverage report defaults in `pyproject.toml` without forcing coverage
  on unrelated focused pytest runs.
- Added a GitHub Actions workflow that runs the T24 unit subset with
  `pytest-cov` and enforces `--cov-fail-under=90`.
- Added a local PowerShell entrypoint mirroring the CI coverage gate.
- During validation closeout, Docker-backed OPA tests were made isolated per
  evaluation by replacing the shared `.codex_tmp` input mount with
  `--stdin-input`.
- The focused T24 subset explicitly covers:
  - direct safety service canonicalizer and classifier unit behavior
  - safety service canonicalizer and classifier endpoints
  - OPA policy behavior
  - approved response cache replay rules
  - source freshness checks
  - audit event persistence and secret redaction
- No OpenClaw-to-safety end-to-end integration, observability, security review,
  or runbook work was added.

## Validation Handoff

Independent validation has now passed and is recorded in
`validation_reports/t24_unit_ci_validation_2026-05-31.md`.

## Local Validation

```text
powershell -ExecutionPolicy Bypass -File .\scripts\run_t24_unit_ci.ps1
46 passed, 1 warning in 38.96s
TOTAL 435 statements, 4 missed, 66 branches, 99% coverage
Required test coverage of 90% reached. Total coverage: 99.20%
```

```text
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
150 passed, 1 skipped, 1 warning in 52.12s
```

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!
```

## Implementation Validation Results

- `powershell -ExecutionPolicy Bypass -File scripts\run_t24_unit_ci.ps1`
  - Result: `46 passed, 1 warning in 38.96s`
  - Coverage gate: `Required test coverage of 90% reached. Total coverage: 99.20%`
- `.venv\Scripts\python.exe -m pytest -p no:cacheprovider`
  - Result: `150 passed, 1 skipped, 1 warning in 52.12s`
- `.venv\Scripts\python.exe -m ruff check .`
  - Result: `All checks passed!`
