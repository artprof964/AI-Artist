from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from typing import Any, Protocol
from urllib.parse import urlsplit
from uuid import UUID

from pydantic import ValidationError

from backend.audit import redact_audit_value
from backend.connection_settings import GITHUB_TOKEN_ENV_VAR, require_env_value
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
        envelope = _coerce_envelope(request.execution_envelope)
        _validate_execution_envelope(envelope, target=request.target, now=now)
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


def _coerce_envelope(
    envelope: ExecutionEnvelopeResponse | dict[str, Any] | None,
) -> ExecutionEnvelopeResponse:
    if envelope is None:
        raise GitHubExecutionGateError("GitHub write requires an execution envelope")

    if isinstance(envelope, ExecutionEnvelopeResponse):
        return envelope

    try:
        return ExecutionEnvelopeResponse.model_validate(envelope)
    except ValidationError as exc:
        raise GitHubExecutionGateError("execution envelope is invalid") from exc


def _validate_execution_envelope(
    envelope: ExecutionEnvelopeResponse,
    *,
    target: str,
    now: datetime | None = None,
) -> None:
    if envelope.operation != GITHUB_WRITE_OPERATION:
        raise GitHubExecutionGateError(
            "execution envelope operation must be github_write"
        )

    if envelope.target != target:
        raise GitHubExecutionGateError(
            "execution envelope target does not match GitHub target"
        )

    if not envelope.valid:
        raise GitHubExecutionGateError("execution envelope is not valid")

    if not envelope.allow:
        raise GitHubExecutionGateError("execution envelope does not allow execution")

    if envelope.requires_human_approval and not envelope.human_approval.approved:
        raise GitHubExecutionGateError("execution envelope requires human approval")

    if not envelope.signature:
        raise GitHubExecutionGateError("execution envelope must include a signature")

    comparison_time = _as_aware_utc(now or datetime.now(timezone.utc))
    expires_at = _as_aware_utc(envelope.expires_at)
    if expires_at <= comparison_time:
        raise GitHubExecutionGateError("execution envelope is expired")


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


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


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
