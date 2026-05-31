import pytest

from backend.payload_fields import (
    PayloadFieldError,
    optional_string_field,
    optional_string_field_message,
    required_mapping_field,
    required_mapping_field_message,
    required_string_field,
    required_string_field_message,
    string_field_or_none,
)


class CustomPayloadError(ValueError):
    pass


def test_required_string_field_returns_present_non_empty_string() -> None:
    assert required_string_field({"channel": "C123"}, "channel") == "C123"


@pytest.mark.parametrize("value", [None, "", "   ", 123])
def test_required_string_field_rejects_missing_blank_or_non_string_values(value: object) -> None:
    with pytest.raises(PayloadFieldError, match=required_string_field_message("channel")):
        required_string_field({"channel": value}, "channel")


def test_required_string_field_allows_custom_error_type_and_message() -> None:
    with pytest.raises(CustomPayloadError, match="custom required message"):
        required_string_field(
            {},
            "filename",
            error_type=CustomPayloadError,
            message="custom required message",
        )


def test_optional_string_field_returns_none_for_missing_or_empty_string_by_default() -> None:
    assert optional_string_field({}, "thread_ts") is None
    assert optional_string_field({"thread_ts": ""}, "thread_ts") is None


def test_optional_string_field_can_preserve_empty_strings() -> None:
    assert optional_string_field({"subfolder": ""}, "subfolder", empty_as_none=False) == ""


def test_optional_string_field_rejects_non_string_values() -> None:
    with pytest.raises(PayloadFieldError, match=optional_string_field_message("thread_ts")):
        optional_string_field({"thread_ts": 123}, "thread_ts")


def test_string_field_or_none_ignores_missing_or_non_string_values() -> None:
    assert string_field_or_none({}, "actor_scope") is None
    assert string_field_or_none({"actor_scope": 123}, "actor_scope") is None
    assert string_field_or_none({"actor_scope": "user:local"}, "actor_scope") == "user:local"


def test_required_mapping_field_returns_nested_mapping() -> None:
    event = {"channel": "C123"}

    assert required_mapping_field({"event": event}, "event") == event


def test_required_mapping_field_rejects_missing_or_non_mapping_values() -> None:
    with pytest.raises(PayloadFieldError, match=required_mapping_field_message("event")):
        required_mapping_field({"event": "not-object"}, "event")


def test_payload_field_validation_messages_are_centralized() -> None:
    assert required_string_field_message("channel") == "payload field 'channel' must be a non-empty string"
    assert optional_string_field_message("thread_ts") == "payload field 'thread_ts' must be a string when present"
    assert required_mapping_field_message("event") == "payload field 'event' must be an object"
