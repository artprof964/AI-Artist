from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Protocol
from uuid import UUID

from backend.adapter_results import targeted_result_fields
from backend.audit import redact_audit_value
from backend.connection_settings import (
    GITHUB_TOKEN_ENV_VAR,
    load_connection_settings,
    require_env_value,
    runtime_env,
)
from backend.execution_gate import require_execution_envelope
from backend.http_methods import normalize_http_write_method
from backend.operations import OPERATION_GITHUB_WRITE
from backend.schemas import ExecutionEnvelopeResponse
from backend.secret_redaction import redact_secret_value
from backend.url_utils import safe_relative_api_path


GITHUB_WRITE_OPERATION = OPERATION_GITHUB_WRITE


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
        env: Mapping[str, str] | None = None,
    ) -> None:
        self._client = client
        self._token_env_var = token_env_var
        self._env = env

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
        method = normalize_http_write_method(
            request.method,
            error_type=GitHubExecutionGateError,
            type_message="GitHub API method must be a string",
            allowed_message="GitHub adapter only permits write methods",
        )
        path = _normalize_api_path(request.path)

        token = self._read_runtime_token()
        client_response = self._client.request(
            method=method,
            path=path,
            json=request.payload,
            token=token,
        )
        safe_client_response = redact_secret_value(
            redact_audit_value(client_response),
            explicit_secrets=(token,),
        )
        result_fields = targeted_result_fields(
            envelope=envelope,
            target=request.target,
            client_response=safe_client_response,
        )

        return GitHubWriteResult(
            execution_envelope_id=result_fields.execution_envelope_id,
            request_id=result_fields.request_id,
            operation=result_fields.operation,
            target=result_fields.target,
            method=method,
            path=path,
            client_response=result_fields.client_response,
        )

    def _read_runtime_token(self) -> str:
        try:
            values = runtime_env(self._env)
            if self._token_env_var == GITHUB_TOKEN_ENV_VAR:
                token = load_connection_settings(values).github_token
                if not token:
                    raise RuntimeError(
                        f"{GITHUB_TOKEN_ENV_VAR} is required for GitHub adapter execution"
                    )
                return token.strip()

            return require_env_value(
                values,
                self._token_env_var,
                purpose="GitHub adapter execution",
            ).strip()
        except RuntimeError as exc:
            raise GitHubAdapterConfigurationError(str(exc)) from exc

def _normalize_api_path(path: str) -> str:
    return safe_relative_api_path(
        path,
        error_type=GitHubExecutionGateError,
        type_message="GitHub API path must be a string",
        absolute_message="GitHub API path must not be an absolute URL",
        relative_message="GitHub API path must be relative and start with /",
        slash_message="GitHub API path must use forward slashes",
        control_message="GitHub API path must not contain control characters",
        traversal_message="GitHub API path must not contain traversal segments",
    )


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
