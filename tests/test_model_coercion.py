import pytest
from pydantic import BaseModel, Field
from pathlib import Path

from backend.model_coercion import ModelCoercionError, coerce_model
from backend.repo_paths import (
    backend_module_filenames,
    backend_module_path,
    read_backend_module_text,
    repo_root_from,
)


REPO_ROOT = repo_root_from(Path(__file__))


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
    allowed = {"model_coercion.py"}
    for module_filename in backend_module_filenames(REPO_ROOT):
        if module_filename in allowed:
            continue
        source = read_backend_module_text(module_filename, REPO_ROOT)
        if ".model_validate(" in source:
            offenders.append(str(backend_module_path(module_filename)))

    assert offenders == []
