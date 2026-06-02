# NP01/NP02 Foundation Slice Progress - 2026-06-01

## Scope

Prepare the testing and update lane for the first next-phase implementation
slice after completed T01-T28 work.

Source docs reviewed:

- `validation_reports/project_review_summary_and_optimization_proposals_2026-06-01.md`
- `validation_reports/standardization_process_review_2026-06-01.md`
- `validation_reports/final_project_validation_2026-06-01.md`
- `docs/final_stack_specs_latest_v1.md`
- `docs/backend_stack_setup_latest_v1.md`
- `local-ai-agent-system-latest-source/docs/project_status_latest_v1.md`

Pre-slice baseline from reviewed docs: T01-T28 remain complete, final pytest
was 553 passed with 1 warning, ruff was clean, and the reviewed next-phase
roadmap starts with NP01 composition root plus NP02 adapter connection/client
factory.

Current NP01/NP02 implementation baseline: focused NP01 and NP02 suites pass,
full ruff passes, and full pytest is 564 passed with 1 warning.

## Planned Implementation Scope

- NP01: introduce a composition root / dependency container for default
  repositories, clients, telemetry, app state, clock providers, and ID
  providers.
- NP02: introduce a shared adapter connection/client factory for Slack, GitHub,
  ComfyUI, Publishing, and LLM smoke paths.
- Keep T01-T28 closed. This slice is next-phase optimization work, not reopened
  foundation implementation.
- Keep NP03-NP08 out of scope except where NP01 must leave a clean dependency
  boundary for later injectable app state, repository protocols, clock/id
  provider expansion, gated-adapter protocol work, source-text test cleanup, and
  registry-driven docs validation.

## Acceptance Gates

- Only the composition boundary constructs local or in-memory defaults; focused
  guards should prevent new direct default construction outside that boundary.
- Endpoint/app tests prove isolated dependency sets and preserve current Safety
  Service route, response, audit, cache, source, provenance, and telemetry
  behavior.
- Adapter tests prove the shared factory covers explicit secrets, env secrets,
  custom env names, default URLs/models, injected clients, missing-secret errors,
  and request/response redaction.
- Slack, GitHub, ComfyUI, Publishing, and LLM smoke paths keep their existing
  domain-facing behavior while using the shared connection/client boundary.
- Focused pytest passes, focused ruff passes, `ruff check .` passes, and the
  full pytest suite passes after integration.

## Validation Results

Focused NP01 pytest:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_composition.py tests\test_safety_service_endpoints.py tests\test_safety_service_units.py tests\test_audit_event_log.py tests\test_response_cache.py tests\test_source_freshness.py tests\test_source_ingestion.py tests\test_knowledge_agent.py tests\test_image_provenance.py tests\test_observability.py -q -p no:cacheprovider
```

Result:

```text
121 passed, 1 warning in 1.31s
```

Focused NP02 pytest:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_adapter_factory.py tests\test_connection_settings.py tests\test_adapter_secrets.py tests\test_secret_redaction.py tests\test_slack_adapter.py tests\test_slack_contracts.py tests\test_github_adapter.py tests\test_github_contracts.py tests\test_comfyui_adapter.py tests\test_comfyui_contracts.py tests\test_publishing_adapter.py tests\test_publishing_agent.py tests\test_publishing_contracts.py tests\test_llm_api_smoke.py -q -p no:cacheprovider -k "not live_llm_api_smoke_test_records_id_and_model_without_secret"
```

Result:

```text
149 passed, 1 deselected in 1.18s
```

Focused ruff:

```powershell
.\.venv\Scripts\python.exe -m ruff check backend tests
```

Result:

```text
All checks passed!
```

Full ruff:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Result:

```text
All checks passed!
```

Full pytest:

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result:

```text
564 passed, 1 warning in 28.31s
```

Optional CI parity check when the service boundary or T24 gate changes:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_t24_unit_ci.ps1
```

Result:

```text
Not run for this slice; full pytest and ruff passed.
```

## Update Notes

- NP01/NP02 implementation started with `backend/composition.py`,
  `backend/adapter_factory.py`, `tests/test_composition.py`, and
  `tests/test_adapter_factory.py`.
- `backend/app.py` now exposes `create_app(composition_root=...)` while keeping
  the default module-level `app` for compatibility.
- Audit endpoints are the first app route wired through composition state:
  `create_app` routes audit records through `root.audit.repository`, and
  focused tests prove two app instances keep audit records isolated.
- Existing direct global hook points remain documented in
  `tests/test_composition.py` as follow-up integration work for later NP01/NP03
  slices.
- Full test count increased from 553 to 564 through the new NP01/NP02 coverage.
