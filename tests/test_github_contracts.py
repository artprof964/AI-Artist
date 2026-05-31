from backend.connection_settings import GITHUB_TOKEN_ENV_VAR
from backend.github_contracts import (
    GITHUB_ADAPTER_EXECUTION_PURPOSE,
    GITHUB_API_METHOD_ALLOWED_MESSAGE,
    GITHUB_API_METHOD_TYPE_MESSAGE,
    GITHUB_API_PATH_ABSOLUTE_MESSAGE,
    GITHUB_API_PATH_CONTROL_MESSAGE,
    GITHUB_API_PATH_RELATIVE_MESSAGE,
    GITHUB_API_PATH_SLASH_MESSAGE,
    GITHUB_API_PATH_TRAVERSAL_MESSAGE,
    GITHUB_API_PATH_TYPE_MESSAGE,
    GITHUB_TARGET_LABEL,
    GITHUB_WRITE_ACTION_LABEL,
    github_token_required,
)
from path_helpers import read_backend_source


def test_github_contracts_preserve_adapter_text() -> None:
    assert GITHUB_WRITE_ACTION_LABEL == "GitHub write"
    assert GITHUB_TARGET_LABEL == "GitHub target"
    assert GITHUB_ADAPTER_EXECUTION_PURPOSE == "GitHub adapter execution"
    assert GITHUB_API_METHOD_TYPE_MESSAGE == "GitHub API method must be a string"
    assert GITHUB_API_METHOD_ALLOWED_MESSAGE == "GitHub adapter only permits write methods"
    assert GITHUB_API_PATH_TYPE_MESSAGE == "GitHub API path must be a string"
    assert GITHUB_API_PATH_ABSOLUTE_MESSAGE == "GitHub API path must not be an absolute URL"
    assert GITHUB_API_PATH_RELATIVE_MESSAGE == "GitHub API path must be relative and start with /"
    assert GITHUB_API_PATH_SLASH_MESSAGE == "GitHub API path must use forward slashes"
    assert GITHUB_API_PATH_CONTROL_MESSAGE == "GitHub API path must not contain control characters"
    assert GITHUB_API_PATH_TRAVERSAL_MESSAGE == "GitHub API path must not contain traversal segments"
    assert (
        github_token_required(GITHUB_TOKEN_ENV_VAR)
        == f"{GITHUB_TOKEN_ENV_VAR} is required for GitHub adapter execution"
    )


def test_github_adapter_uses_shared_contract_messages() -> None:
    source = read_backend_source("github_adapter.py")

    forbidden_literals = [
        '"GitHub write"',
        '"GitHub target"',
        '"GitHub API method must be a string"',
        '"GitHub adapter only permits write methods"',
        '"GitHub API path must be a string"',
        '"GitHub API path must not be an absolute URL"',
        '"GitHub API path must be relative and start with /"',
        '"GitHub API path must use forward slashes"',
        '"GitHub API path must not contain control characters"',
        '"GitHub API path must not contain traversal segments"',
        '"GitHub adapter execution"',
        "is required for GitHub adapter execution",
    ]
    for literal in forbidden_literals:
        assert literal not in source
    assert "GITHUB_WRITE_ACTION_LABEL" in source
    assert "GITHUB_TARGET_LABEL" in source
    assert "GITHUB_API_METHOD_TYPE_MESSAGE" in source
    assert "GITHUB_API_METHOD_ALLOWED_MESSAGE" in source
    assert "GITHUB_API_PATH_TYPE_MESSAGE" in source
    assert "GITHUB_ADAPTER_EXECUTION_PURPOSE" in source
    assert "adapter_runtime_secret(" in source
