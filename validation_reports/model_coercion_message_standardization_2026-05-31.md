# Model Coercion Message Standardization - 2026-05-31

## Scope

Centralized default Pydantic model coercion error messages behind a shared helper.

## Changes

- Added `model_payload_invalid_message(...)` to `backend/model_coercion.py`.
- Routed `coerce_model(...)` default validation failures through the shared helper.
- Added tests for the shared message helper and a source guard against inline raise-site formatting.

## Validation

```text
pytest tests\test_model_coercion.py tests\test_subagent_output_contracts.py tests\test_image_provenance.py tests\test_critic_curator.py tests\test_execution_gate.py -q -p no:cacheprovider
47 passed in 0.22s

ruff check backend\model_coercion.py tests\test_model_coercion.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. Model coercion failure text now flows through a shared helper.
