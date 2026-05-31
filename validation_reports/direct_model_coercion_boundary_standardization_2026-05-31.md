# Direct Model Coercion Boundary Standardization - 2026-05-31

## Scope

`backend/image_provenance.py` and `backend/critic_curator.py` now call
`backend.model_coercion.coerce_model` directly at their domain input
boundaries.

The local `_coerce_provenance_input` and `_coerce_metadata` wrappers were
removed so Pydantic model/dict coercion remains centralized in
`backend/model_coercion.py`.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_image_provenance.py tests\test_critic_curator.py tests\test_model_coercion.py tests\test_critic_rubric.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\image_provenance.py backend\critic_curator.py tests\test_image_provenance.py tests\test_critic_curator.py
```

## Result

```text
32 passed
All checks passed!
Full suite: 329 passed, 1 skipped, 1 warning
```

## Guard

The image provenance and critic/curator tests check that the local `_coerce_*`
wrappers are not reintroduced and that the modules call `coerce_model`
directly.
