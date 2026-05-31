# T24 Unit CI Validation - 2026-05-31

## Result

Pass. T24 safety unit CI is independently validated.

## Acceptance Checked

- The local T24 gate runs canonicalizer, classifier, OPA policy behavior,
  response cache, source freshness, audit event log, and safety endpoint tests.
- The CI workflow runs the same focused safety unit coverage gate and
  repository lint.
- The coverage threshold is enforced by `pytest-cov` with
  `--cov-fail-under=90` and explicit module targets:
  `backend.app`, `backend.audit`, `backend.response_cache`, `backend.schemas`,
  `backend.service`, and `backend.source_freshness`.
- `scripts/run_t24_unit_ci.ps1` propagates native pytest failures through
  `Invoke-NativeCommand` and `$LASTEXITCODE`.
- OPA policy tests pass input through `opa eval --stdin-input`, avoiding a
  transient Windows temp-file mount for policy input.
- T24 status docs mark T24 complete and T25 next. Existing T25/T26 artifacts in
  the dirty worktree were not implemented or modified for this T24 closeout.

## Files Inspected

- `pyproject.toml`
- `requirements.txt`
- `scripts/run_t24_unit_ci.ps1`
- `.github/workflows/t24-safety-unit-ci.yml`
- `tests/test_safety_service_units.py`
- `tests/test_safety_service_endpoints.py`
- `tests/test_opa_policy.py`
- `tests/test_response_cache.py`
- `tests/test_source_freshness.py`
- `tests/test_audit_event_log.py`

## Commands Run

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_t24_unit_ci.ps1
```

Result: pass.

```text
46 passed, 1 warning in 38.96s
TOTAL 435 statements, 4 missed, 66 branches, 99% coverage
Required test coverage of 90% reached. Total coverage: 99.20%
```

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result: pass.

```text
150 passed, 1 skipped, 1 warning in 52.12s
```

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Result: pass.

```text
All checks passed!
```

## Tracker And Status

- `project_status_latest_v1.md`: T24 complete, 24 complete / 4 open, T25 next.
- `task_validation_matrix_latest_v1.md`: T24 Bestanden with
  `--cov-fail-under=90`; T25 Ausstehend.
- `README.md` and `overview_project_outline_params_latest_v2.md`: T24 passed,
  T25 next.
- `AI_Artist_Agent_Projekttracker.xlsx`: not modified in this closeout because
  the spreadsheet skill's required `@oai/artifact-tool` runtime was unavailable
  in the current Node environment.

## Residual Risks

- OPA tests still depend on Docker and the `openpolicyagent/opa:0.70.0` image.
- Full pytest emits a Starlette `TestClient` deprecation warning; it does not
  fail validation.
- The worktree was dirty before validation began and continued changing during
  validation; this report is scoped to T24 changes and command results.
