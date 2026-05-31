# T19 Critic/Curator Rubrics Validation

## Scope

Implemented deterministic local Critic/Curator rubric scoring for generated image metadata.

## Acceptance Criteria

- Scores mocked image metadata without network calls, LLM API calls, Slack, or publishing integrations.
- Returns structured critique by rubric category.
- Returns deterministic pass/fail decisions.
- Returns improvement notes for failed rubric categories.
- Includes all rubric categories from `workspaces/critic-curator/rubrics/image_quality.md`:
  - prompt adherence
  - composition
  - visual originality
  - artifact severity
  - source/provenance completeness
  - publication readiness
- Uses `ImageProvenanceRecord` metadata for source/provenance completeness.
- Supports ordered batch scoring for multiple image candidates.

## Independent Validation

```text
.\.venv\Scripts\python.exe -m pytest tests\test_critic_curator.py -q -p no:cacheprovider
5 passed in 0.11s
```

```text
.\.venv\Scripts\python.exe -m ruff check backend\critic_curator.py tests\test_critic_curator.py
All checks passed!
```

```text
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
112 passed, 1 skipped, 1 warning in 44.30s
```

The full-suite warning is the existing Starlette/httpx test client deprecation warning:
`Using httpx with starlette.testclient is deprecated; install httpx2 instead.`

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!
```

## Verdict

T19 passes independent validation. `backend/critic_curator.py` returns a structured
`CriticCuratorResult` with one score per Markdown rubric category, deterministic
pass/fail decisions, failed-category improvement notes, provenance completeness
sensitivity through `ImageProvenanceRecord`, and deterministic batch ordering.

## Residual Risk

The provenance rubric currently scores required field presence and review status
shape. It does not verify that the attached provenance `image_id` matches the
scored metadata `image_id`, nor does it validate storage URI reachability.
