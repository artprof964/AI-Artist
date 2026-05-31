# T12 Mock Sub-Agent Orchestration Validation

Independent validation refreshed on 2026-05-31.

## Scope

Implemented deterministic local mock sub-agent orchestration in
`backend/orchestrator.py`.

This task did not implement T13+ cache replay, source freshness persistence,
real retrieval, ComfyUI execution, external publishing, or network/API calls.

## Contract

The mock orchestrator routes a single `MockAgentRequest` through three local
mock agents:

- `knowledge`
- `image_planner`
- `critic_curator`

Each mock agent returns the existing `SubAgentOutput` schema from
`backend/schemas.py`. The synthesized result aggregates:

- status and status counts
- per-agent summaries
- artifacts
- sources
- policy notes
- average confidence
- structured errors

Status synthesis uses the most severe returned status in this order:
`ok`, `needs_retry`, `blocked`, `failed`.

## Validation

Focused orchestration test:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_mock_subagents.py -p no:cacheprovider
3 passed in 0.12s
```

Full test suite:

```text
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
56 passed, 1 skipped, 1 warning in 45.06s
```

Lint:

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!
```

## Acceptance Criteria

- One request is routed through all mock agents.
- Every mock agent output is validated as `SubAgentOutput`.
- The synthesized result includes aggregated status, summaries, artifacts,
  sources, policy notes, confidence, and errors.
- Mock agents are deterministic and local.
- No T13+ behavior was implemented.

## Result

T12 passed on 2026-05-31.
