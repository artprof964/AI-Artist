# Slack Adapter Helper Standardization

Date: 2026-06-01

## Scope

Added `tests/slack_adapter_helpers.py` for Slack adapter test setup.

The helper owns the deterministic Slack client double, inbound event payload,
channel/user/team/event IDs, timestamps, and normalized request text used by
Slack adapter tests. The adapter test module now guards against reintroducing a
local `MockSlackClient` class or local Slack event payload builder.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check tests\slack_adapter_helpers.py tests\test_slack_adapter.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_slack_adapter.py -q -p no:cacheprovider
14 passed
```

## Alignment Result

Slack adapter tests now share connection env setup, Slack client doubles, event
payloads, event identity values, timestamps, and normalized text through shared
test helpers.
