import pytest

from backend.response_fields import (
    RESPONSE_CHOICES_FIELD,
    RESPONSE_CONTENT_FIELD,
    RESPONSE_ENTRY_OBJECT_MESSAGE,
    RESPONSE_ID_FIELD,
    RESPONSE_MESSAGE_FIELD,
    RESPONSE_MODEL_FIELD,
    ResponseFieldError,
    field_value,
    first_choice_message_content,
    required_response_list,
    required_response_list_message,
    require_response_mapping,
)


class SDKMessage:
    choices = [{"message": {"content": "hello"}}]


def test_field_value_reads_mapping_and_sdk_object_shapes() -> None:
    assert field_value({"id": "resp_123"}, "id") == "resp_123"
    assert field_value(SDKMessage(), "choices")[0]["message"]["content"] == "hello"
    assert field_value(SDKMessage(), "missing", "fallback") == "fallback"


def test_first_choice_message_content_reads_mapping_and_sdk_object_shapes() -> None:
    assert first_choice_message_content(
        {"choices": [{"message": {"content": "hello from mapping"}}]}
    ) == "hello from mapping"
    assert first_choice_message_content(SDKMessage()) == "hello"
    assert first_choice_message_content({"choices": []}) is None


def test_required_response_list_accepts_non_empty_lists() -> None:
    assert required_response_list({"images": [{"filename": "one.png"}]}, "images") == [
        {"filename": "one.png"}
    ]


@pytest.mark.parametrize("value", [None, [], "not-list"])
def test_required_response_list_rejects_missing_empty_or_wrong_shape(value: object) -> None:
    with pytest.raises(ResponseFieldError, match=required_response_list_message("images")):
        required_response_list({"images": value}, "images")


def test_require_response_mapping_rejects_non_objects() -> None:
    with pytest.raises(ResponseFieldError, match=RESPONSE_ENTRY_OBJECT_MESSAGE):
        require_response_mapping("not-object")


def test_response_validation_messages_are_centralized() -> None:
    assert required_response_list_message("images") == "response field 'images' must be a non-empty list"
    assert RESPONSE_ENTRY_OBJECT_MESSAGE == "response entry must be an object"


def test_provider_response_field_names_are_centralized() -> None:
    assert RESPONSE_ID_FIELD == "id"
    assert RESPONSE_MODEL_FIELD == "model"
    assert RESPONSE_CHOICES_FIELD == "choices"
    assert RESPONSE_MESSAGE_FIELD == "message"
    assert RESPONSE_CONTENT_FIELD == "content"
