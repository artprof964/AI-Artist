from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
from typing import Any, Protocol
from urllib.parse import urlsplit
from uuid import UUID

from backend.audit import redact_audit_value
from backend.connection_settings import GITHUB_TOKEN_ENV_VAR, require_env_value
from backend.execution_gate import require_execution_envelope
from backend.schemas import ExecutionEnvelopeResponse


GITHUB_WRITE_OPERATION = "github_write"


class GitHubExecutionGateError(PermissionError):
    """Raised when GitHub execution is attempted without an approved envelope."""


class GitHubAdapterConfigurationError(RuntimeError):
    """Raised when the adapter cannot read its runtime GitHub token."""


class GitHubAPIClient(Protocol):
    def request(
        self,
        *,
        method: str,
        path: str,
        json: dict[str, Any],
        token: str,
    ) -> dict[str, Any]:
        """Perform a GitHub API request and return the client response."""


@dataclass(frozen=True)
class GitHubWriteRequest:
    method: str
    path: str
    payload: dict[str, Any]
    target: str
    execution_envelope: ExecutionEnvelopeResponse | dict[str, Any] | None


@dataclass(frozen=True)
class GitHubWriteResult:
    execution_envelope_id: UUID
    request_id: UUID
    operation: str
    target: str
    method: str
    path: str
    client_response: dict[str, Any]


class GitHubAdapter:
    def __init__(
        self,
        client: GitHubAPIClient,
        *,
        token_env_var: str = GITHUB_TOKEN_ENV_VAR,
    ) -> None:
        self._client = client
        self._token_env_var = token_env_var

    def write(
        self,
        request: GitHubWriteRequest,
        *,
        now: datetime | None = None,
    ) -> GitHubWriteResult:
        envelope = require_execution_envelope(
            request.execution_envelope,
            operation=GITHUB_WRITE_OPERATION,
            missing_message="GitHub write requires an execution envelope",
            error_type=GitHubExecutionGateError,
            target=request.target,
            target_label="GitHub target",
            require_human_approval_when_marked=True,
            now=now,
        )
        method = _normalize_write_method(request.method)
        path = _normalize_api_path(request.path)

        token = self._read_runtime_token()
        client_response = self._client.request(
            method=method,
            path=path,
            json=request.payload,
            token=token,
        )
        safe_client_response = _redact_secret(redact_audit_value(client_response), token)

        return GitHubWriteResult(
            execution_envelope_id=envelope.execution_envelope_id,
            request_id=envelope.request_id,
            operation=envelope.operation,
            target=request.target,
            method=method,
            path=path,
            client_response=safe_client_response,
        )

    def _read_runtime_token(self) -> str:
        try:
            return require_env_value(
                os.environ,
                self._token_env_var,
                purpose="GitHub adapter execution",
            ).strip()
        except RuntimeError as exc:
            raise GitHubAdapterConfigurationError(str(exc)) from exc

def _normalize_write_method(method: str) -> str:
    if not isinstance(method, str):
        raise GitHubExecutionGateError("GitHub API method must be a string")

    normalized = method.strip().upper()
    if normalized not in {"POST", "PATCH", "PUT", "DELETE"}:
        raise GitHubExecutionGateError("GitHub adapter only permits write methods")
    return normalized


def _normalize_api_path(path: str) -> str:
    if not isinstance(path, str):
        raise GitHubExecutionGateError("GitHub API path must be a string")

    normalized = path.strip()
    split_path = urlsplit(normalized)
    if split_path.scheme or split_path.netloc:
        raise GitHubExecutionGateError("GitHub API path must not be an absolute URL")
    if not split_path.path.startswith("/"):
        raise GitHubExecutionGateError("GitHub API path must be relative and start with /")
    if "\\" in normalized:
        raise GitHubExecutionGateError("GitHub API path must use forward slashes")
    if any(ord(character) < 32 for character in normalized):
        raise GitHubExecutionGateError("GitHub API path must not contain control characters")
    if any(segment in {".", ".."} for segment in split_path.path.split("/")):
        raise GitHubExecutionGateError("GitHub API path must not contain traversal segments")
    return normalized


def _redact_secret(value: Any, secret: str) -> Any:
    if isinstance(value, dict):
        return {key: _redact_secret(nested, secret) for key, nested in value.items()}

    if isinstance(value, list):
        return [_redact_secret(item, secret) for item in value]

    if isinstance(value, str) and secret:
        return value.replace(secret, "[REDACTED]")

    return value

__all__ = [
    "GITHUB_TOKEN_ENV_VAR",
    "GITHUB_WRITE_OPERATION",
    "GitHubAPIClient",
    "GitHubAdapter",
    "GitHubAdapterConfigurationError",
    "GitHubExecutionGateError",
    "GitHubWriteRequest",
    "GitHubWriteResult",
]
