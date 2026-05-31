from __future__ import annotations


SLACK_SOURCE = "slack"


def slack_event_object_required() -> str:
    return "Slack payload must include an event object"


def slack_required_string_field(field_name: str) -> str:
    return f"Slack event field {field_name!r} must be a non-empty string"


def slack_optional_string_field(field_name: str) -> str:
    return f"Slack event field {field_name!r} must be a string when present"


def slack_response_text_required() -> str:
    return "Slack response text must be non-empty"


__all__ = [
    "SLACK_SOURCE",
    "slack_event_object_required",
    "slack_optional_string_field",
    "slack_required_string_field",
    "slack_response_text_required",
]
