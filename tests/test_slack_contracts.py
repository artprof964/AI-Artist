from backend.repo_paths import read_backend_module_text
from backend.slack_contracts import (
    SLACK_ADAPTER_EXECUTION_PURPOSE,
    SLACK_SOURCE,
    slack_event_object_required,
    slack_optional_string_field,
    slack_required_string_field,
    slack_response_text_required,
)


def test_slack_contracts_preserve_message_text() -> None:
    assert SLACK_SOURCE == "slack"
    assert SLACK_ADAPTER_EXECUTION_PURPOSE == "Slack adapter execution"
    assert slack_event_object_required() == "Slack payload must include an event object"
    assert (
        slack_required_string_field("channel")
        == "Slack event field 'channel' must be a non-empty string"
    )
    assert (
        slack_optional_string_field("thread_ts")
        == "Slack event field 'thread_ts' must be a string when present"
    )
    assert slack_response_text_required() == "Slack response text must be non-empty"


def test_slack_adapter_uses_shared_contract_messages() -> None:
    source = read_backend_module_text("slack_adapter.py")

    forbidden_literals = [
        '"Slack payload must include an event object"',
        '"Slack event field',
        '"Slack response text must be non-empty"',
        '"Slack adapter execution"',
        'source: str = "slack"',
    ]
    for literal in forbidden_literals:
        assert literal not in source
    assert "slack_event_object_required()" in source
    assert "slack_required_string_field(" in source
    assert "slack_optional_string_field(" in source
    assert "slack_response_text_required()" in source
    assert "source: str = SLACK_SOURCE" in source
    assert "SLACK_ADAPTER_EXECUTION_PURPOSE" in source
