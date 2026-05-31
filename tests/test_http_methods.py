import pytest

from backend.http_methods import (
    HTTP_METHOD_DELETE,
    HTTP_METHOD_PATCH,
    HTTP_METHOD_POST,
    HTTP_METHOD_PUT,
    HTTP_WRITE_METHODS,
    HTTPMethodError,
    normalize_http_method,
    normalize_http_write_method,
)
from backend.repo_paths import read_backend_module_text


class CustomHTTPMethodError(ValueError):
    pass


def test_http_write_method_vocabulary_is_centralized() -> None:
    assert HTTP_WRITE_METHODS == frozenset(
        {
            HTTP_METHOD_POST,
            HTTP_METHOD_PATCH,
            HTTP_METHOD_PUT,
            HTTP_METHOD_DELETE,
        }
    )


def test_normalize_http_write_method_trims_uppercases_and_accepts_writes() -> None:
    assert normalize_http_write_method(" post ") == HTTP_METHOD_POST
    assert normalize_http_write_method("PATCH") == HTTP_METHOD_PATCH
    assert normalize_http_write_method("put") == HTTP_METHOD_PUT
    assert normalize_http_write_method("delete") == HTTP_METHOD_DELETE


@pytest.mark.parametrize("method", ["GET", "HEAD", "OPTIONS", "", "   "])
def test_normalize_http_write_method_rejects_non_write_methods(method: str) -> None:
    with pytest.raises(HTTPMethodError, match="write method"):
        normalize_http_write_method(method)


def test_normalize_http_method_allows_custom_error_type_and_messages() -> None:
    with pytest.raises(CustomHTTPMethodError, match="custom type"):
        normalize_http_method(
            123,  # type: ignore[arg-type]
            allowed_methods={HTTP_METHOD_POST},
            error_type=CustomHTTPMethodError,
            type_message="custom type",
        )

    with pytest.raises(CustomHTTPMethodError, match="custom allowed"):
        normalize_http_method(
            "GET",
            allowed_methods={HTTP_METHOD_POST},
            error_type=CustomHTTPMethodError,
            allowed_message="custom allowed",
        )


def test_github_adapter_uses_shared_http_method_boundary() -> None:
    source = read_backend_module_text("github_adapter.py")

    assert "from backend.http_methods import normalize_http_write_method" in source
    assert "def _normalize_write_method(" not in source
    assert '{"POST", "PATCH", "PUT", "DELETE"}' not in source
