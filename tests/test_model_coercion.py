import pytest
from pydantic import BaseModel, Field
from pathlib import Path

from backend.model_coercion import ModelCoercionError, coerce_model


REPO_ROOT = Path(__file__).resolve().parents[1]


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


def test_backend_domain_code_uses_shared_model_coercion_boundary() -> None:
    offenders: list[str] = []
    allowed = {REPO_ROOT / "backend" / "model_coercion.py"}
    for path in (REPO_ROOT / "backend").glob("*.py"):
        if path in allowed:
            continue
        source = path.read_text(encoding="utf-8")
        if ".model_validate(" in source:
            offenders.append(str(path.relative_to(REPO_ROOT)))

    assert offenders == []
