# Publishing Scope Default Standardization - 2026-05-31

## Scope

Centralized Publishing Agent actor and policy scope defaults behind the shared
request-scope contract.

## Changes

- Added `DEFAULT_PUBLISHING_ACTOR_SCOPE` and
  `DEFAULT_PUBLISHING_POLICY_SCOPE` to `backend/request_scope_contracts.py`.
- Updated `backend/publishing.py` so `PublishingAgentRequest` defaults use the
  shared publishing scope constants.
- Added a Publishing Agent guard test to prevent local publishing scope literals
  from returning.
- Updated stack, interface, status, validation matrix, manifest, and tracker
  artifacts to record the publishing scope boundary.

## Validation

```text
python -m pytest tests/test_publishing_agent.py tests/test_side_effect_audit.py tests/test_request_metadata.py -q -p no:cacheprovider
9 passed

python -m ruff check backend/request_scope_contracts.py backend/publishing.py tests/test_publishing_agent.py
All checks passed.
```

## Result

Passed. Publishing actor and policy scope defaults now share the same contract
module as schema and mock orchestration request-scope defaults.
