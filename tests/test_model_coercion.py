import pytest
from pydantic import BaseModel, Field

from backend.model_coercion import ModelCoercionError, coerce_model


class ExampleModel(BaseModel):
    name: str = Field(min_length=1)


class CustomCoercionError(ValueError):
    pass


def test_coerce_model_returns_existing_model_instance() -> None:
    value = ExampleModel(name="ready")

    assert coerce_model(value, ExampleModel) is value


def test_coerce_model_validates_dict_payload() -> None:
    assert coerce_model({"name": "ready"}, ExampleModel) == ExampleModel(name="ready")


def test_coerce_model_raises_default_error_for_invalid_payload() -> None:
    with pytest.raises(ModelCoercionError, match="ExampleModel payload is invalid"):
        coerce_model({"name": ""}, ExampleModel)


def test_coerce_model_allows_custom_error_type_and_message() -> None:
    with pytest.raises(CustomCoercionError, match="custom coercion failure"):
        coerce_model(
            {"name": ""},
            ExampleModel,
            error_type=CustomCoercionError,
            message="custom coercion failure",
        )
