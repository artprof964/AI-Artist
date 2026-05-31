# Slack Contract Standardization Validation - 2026-05-31

## Scope

Centralized Slack adapter source labels and validation message text so inbound
event parsing and outbound response formatting use one shared contract boundary.

## Changes

- Added `backend/slack_contracts.py`.
- Updated `backend/slack_adapter.py` to use shared Slack source and validation
  message helpers.
- Added guard tests proving Slack adapter message literals no longer live in the
  adapter implementation.

## Validation

```text
pytest tests/test_slack_contracts.py tests/test_slack_adapter.py tests/test_payload_fields.py tests/test_request_identity.py tests/test_secret_redaction.py -q -p no:cacheprovider
33 passed in 0.09s

ruff check backend/slack_contracts.py backend/slack_adapter.py tests/test_slack_contracts.py tests/test_slack_adapter.py
All checks passed.
```

## Result

Passed. Slack source labels and validation text now flow through
`backend/slack_contracts.py` before adapter errors are raised.
