import pytest

from backend.response_fields import (
    ResponseFieldError,
    field_value,
    required_response_list,
    require_response_mapping,
)


class SDKMessage:
    choices = [{"message": {"content": "hello"}}]


def test_field_value_reads_mapping_and_sdk_object_shapes() -> None:
    assert field_value({"id": "resp_123"}, "id") == "resp_123"
    assert field_value(SDKMessage(), "choices")[0]["message"]["content"] == "hello"
    assert field_value(SDKMessage(), "missing", "fallback") == "fallback"


def test_required_response_list_accepts_non_empty_lists() -> None:
    assert required_response_list({"images": [{"filename": "one.png"}]}, "images") == [
        {"filename": "one.png"}
    ]


@pytest.mark.parametrize("value", [None, [], "not-list"])
def test_required_response_list_rejects_missing_empty_or_wrong_shape(value: object) -> None:
    with pytest.raises(ResponseFieldError, match="images"):
        required_response_list({"images": value}, "images")


def test_require_response_mapping_rejects_non_objects() -> None:
    with pytest.raises(ResponseFieldError, match="object"):
        require_response_mapping("not-object")
