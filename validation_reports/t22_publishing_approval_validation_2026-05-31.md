# T22 Publishing Approval Validation - 2026-05-31

Result: PASS

## Scope

Inspected:
- `backend/publishing.py`
- `backend/publishing_adapter.py`
- `backend/schemas.py`
- `backend/service.py`
- `tests/test_publishing_agent.py`
- `tests/test_publishing_adapter.py`

## Evidence

- `backend/service.py` treats `publish` as a sensitive operation, requires human approval for sensitive operations, and only sets `allow`/`valid` true when source freshness is OK and approval is attached.
- `backend/publishing_adapter.py` validates the execution envelope before invoking the publishing client. It rejects missing/invalid envelopes, wrong operations, target mismatches, invalid/denied envelopes, missing approval, missing signatures, and expired envelopes before `self._client.publish(...)`. It also requires approved human approval for `publish` even if a forged envelope claims human approval is not required.
- `backend/publishing.py` uses an injected publishing client or `LocalPublishingClient`; the local client records calls in process and returns a deterministic `local-publish-...` id derived from target and payload. No real external publishing/API path is present in the validated publishing flow.
- `tests/test_publishing_adapter.py` verifies blocked unapproved publishing leaves `client.calls == []`, approved publishing calls the mock client exactly once, and invalid envelope variants are rejected before client execution.
- `tests/test_publishing_agent.py` verifies the agent records blocked/published audit events, does not call the local client without approval, returns a deterministic local publish id after approval, and redacts sensitive client-response fields in audit events.

## Commands

```powershell
.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests\test_publishing_agent.py tests\test_publishing_adapter.py
```

Result: `12 passed in 0.25s`

```powershell
.venv\Scripts\python.exe -m ruff check backend\publishing_adapter.py backend\publishing.py tests\test_publishing_adapter.py tests\test_publishing_agent.py
```

Result: `All checks passed!`

```powershell
.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests\test_audit_event_log.py tests\test_safety_service_units.py tests\test_safety_service_endpoints.py tests\test_opa_policy.py
```

Result: `26 passed, 1 warning in 82.84s`

```powershell
.venv\Scripts\python.exe -m ruff check .
```

Result: `All checks passed!`

```powershell
.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

Original result: `141 passed, 1 skipped, 1 warning in 70.29s`

Independent validation result: `142 passed, 1 skipped, 1 warning in 99.49s`

Warning: `StarletteDeprecationWarning` from FastAPI/TestClient import path; unrelated to publishing approval behavior.

## Acceptance

Acceptance is satisfied: external/local mocked publishing remains blocked until human approval is attached to a valid execution envelope, forged publish envelopes cannot bypass approval by clearing `requires_human_approval`, and approved publishing proceeds deterministically through local/mock clients without real external publishing/API calls.

## Residual Risk

- The adapter checks that a signature is present but does not independently recompute/verify the HMAC signature contents. This is acceptable for the validated task scope if envelope creation is trusted, but it is a future hardening point.
- Validation covered focused publishing tests, adjacent safety/OPA regressions, repository-wide linting, and the full repository test suite.
