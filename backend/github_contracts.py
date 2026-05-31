from __future__ import annotations

from backend.connection_settings import connection_value_required


GITHUB_WRITE_ACTION_LABEL = "GitHub write"
GITHUB_TARGET_LABEL = "GitHub target"
GITHUB_ADAPTER_EXECUTION_PURPOSE = "GitHub adapter execution"

GITHUB_API_METHOD_TYPE_MESSAGE = "GitHub API method must be a string"
GITHUB_API_METHOD_ALLOWED_MESSAGE = "GitHub adapter only permits write methods"
GITHUB_API_PATH_TYPE_MESSAGE = "GitHub API path must be a string"
GITHUB_API_PATH_ABSOLUTE_MESSAGE = "GitHub API path must not be an absolute URL"
GITHUB_API_PATH_RELATIVE_MESSAGE = "GitHub API path must be relative and start with /"
GITHUB_API_PATH_SLASH_MESSAGE = "GitHub API path must use forward slashes"
GITHUB_API_PATH_CONTROL_MESSAGE = "GitHub API path must not contain control characters"
GITHUB_API_PATH_TRAVERSAL_MESSAGE = "GitHub API path must not contain traversal segments"


def github_token_required(env_var_name: str) -> str:
    return connection_value_required(env_var_name, GITHUB_ADAPTER_EXECUTION_PURPOSE)


__all__ = [
    "GITHUB_ADAPTER_EXECUTION_PURPOSE",
    "GITHUB_API_METHOD_ALLOWED_MESSAGE",
    "GITHUB_API_METHOD_TYPE_MESSAGE",
    "GITHUB_API_PATH_ABSOLUTE_MESSAGE",
    "GITHUB_API_PATH_CONTROL_MESSAGE",
    "GITHUB_API_PATH_RELATIVE_MESSAGE",
    "GITHUB_API_PATH_SLASH_MESSAGE",
    "GITHUB_API_PATH_TRAVERSAL_MESSAGE",
    "GITHUB_API_PATH_TYPE_MESSAGE",
    "GITHUB_TARGET_LABEL",
    "GITHUB_WRITE_ACTION_LABEL",
    "github_token_required",
]
