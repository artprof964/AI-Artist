import pytest

from backend.url_utils import URLValidationError, http_url_domain, safe_relative_api_path


class CustomURLError(ValueError):
    pass


def test_http_url_domain_returns_lowercase_hostname_for_http_urls() -> None:
    assert http_url_domain("https://ART.example/research/palette") == "art.example"


@pytest.mark.parametrize(
    "uri",
    [
        "workspace://ai-artist-main/memory/style.md",
        "https:///missing-host",
        "/relative/path",
    ],
)
def test_http_url_domain_rejects_non_absolute_http_urls(uri: str) -> None:
    with pytest.raises(URLValidationError, match=r"absolute http\(s\) URL"):
        http_url_domain(uri)


def test_http_url_domain_allows_custom_error_type_and_message() -> None:
    with pytest.raises(CustomURLError, match="custom URL message"):
        http_url_domain(
            "workspace://ai-artist-main/memory/style.md",
            error_type=CustomURLError,
            message="custom URL message",
        )


def test_safe_relative_api_path_trims_and_accepts_forward_slash_paths() -> None:
    assert safe_relative_api_path("  /repos/artprof964/AI-Art/issues  ") == (
        "/repos/artprof964/AI-Art/issues"
    )


@pytest.mark.parametrize(
    ("path", "match"),
    [
        ("https://api.github.com/repos/artprof964/AI-Art/issues", "absolute URL"),
        ("//api.github.com/repos/artprof964/AI-Art/issues", "absolute URL"),
        ("repos/artprof964/AI-Art/issues", "start with /"),
        ("/repos\\artprof964\\AI-Art\\issues", "forward slashes"),
        ("/repos/artprof964/AI-Art/issues\n/1", "control characters"),
        ("/repos/artprof964/AI-Art/../issues", "traversal"),
    ],
)
def test_safe_relative_api_path_rejects_unsafe_shapes(path: str, match: str) -> None:
    with pytest.raises(URLValidationError, match=match):
        safe_relative_api_path(path)


def test_safe_relative_api_path_allows_custom_error_messages() -> None:
    with pytest.raises(CustomURLError, match="custom absolute"):
        safe_relative_api_path(
            "https://api.github.com/repos/artprof964/AI-Art/issues",
            error_type=CustomURLError,
            absolute_message="custom absolute",
        )
