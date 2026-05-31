from __future__ import annotations

import ast
from datetime import timedelta
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest

from backend.github_adapter import (
    GITHUB_TOKEN_ENV_VAR,
    GitHubAdapter,
    GitHubAdapterConfigurationError,
    GitHubExecutionGateError,
    GitHubWriteRequest,
)
from backend.repo_paths import (
    backend_module_filenames,
    backend_module_path,
    read_backend_module_text,
    repo_root_from,
)
from backend.schemas import ExecutionEnvelopeRequest, HumanApproval, SourceFreshness
from backend.service import create_execution_envelope
from backend.time_utils import utc_now


REQUEST_ID = UUID("23232323-2323-2323-2323-232323232323")
NOW = utc_now()
GITHUB_TARGET = "github://artprof964/AI-Art/issues"
GITHUB_PATH = "/repos/artprof964/AI-Art/issues"
MOCK_GITHUB_TOKEN = "ghp_mocked_t23_secret_token_1234567890"
PROJECT_ROOT = repo_root_from(Path(__file__))


class MockGitHubAPI:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def request(
        self,
        *,
        method: str,
        path: str,
        json: dict[str, Any],
        token: str,
    ) -> dict[str, Any]:
        self.calls.append(
            {
                "method": method,
                "path": path,
                "json": json,
                "token": token,
            }
        )
        return {
            "id": 123,
            "status": "created",
            "url": "https://api.github.local/repos/artprof964/AI-Art/issues/123",
            "authorization": f"Bearer {token}",
            "debug": {
                "token": token,
                "message": f"mock client echoed {token}",
            },
        }


def approved_envelope(
    *,
    operation: str = "github_write",
    target: str = GITHUB_TARGET,
):
    return create_execution_envelope(
        ExecutionEnvelopeRequest(
            request_id=REQUEST_ID,
            request_kind="action",
            operation=operation,
            requester_scope="user:local",
            policy_scope="workspace:ai-artist-main",
            target=target,
            human_approval=HumanApproval(
                approved=True,
                approver_scope="user:owner",
                approved_at=NOW,
            ),
            source_freshness=SourceFreshness(
                all_required_sources_unchanged=True,
                changed_source_count=0,
            ),
        )
    )


def unapproved_github_write_envelope():
    return create_execution_envelope(
        ExecutionEnvelopeRequest(
            request_id=REQUEST_ID,
            request_kind="action",
            operation="github_write",
            requester_scope="user:local",
            policy_scope="workspace:ai-artist-main",
            target=GITHUB_TARGET,
            human_approval=HumanApproval(approved=False),
            source_freshness=SourceFreshness(
                all_required_sources_unchanged=True,
                changed_source_count=0,
            ),
        )
    )


def github_write_request(*, envelope: object) -> GitHubWriteRequest:
    return GitHubWriteRequest(
        method="post",
        path=GITHUB_PATH,
        payload={
            "title": "T23 local mocked issue",
            "body": "Created through the deterministic mocked GitHub API.",
        },
        target=GITHUB_TARGET,
        execution_envelope=envelope,
    )


def test_github_adapter_uses_mocked_api_and_keeps_token_inside_adapter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(GITHUB_TOKEN_ENV_VAR, MOCK_GITHUB_TOKEN)
    client = MockGitHubAPI()
    adapter = GitHubAdapter(client)
    envelope = approved_envelope()

    result = adapter.write(github_write_request(envelope=envelope), now=NOW)

    assert client.calls == [
        {
            "method": "POST",
            "path": GITHUB_PATH,
            "json": {
                "title": "T23 local mocked issue",
                "body": "Created through the deterministic mocked GitHub API.",
            },
            "token": MOCK_GITHUB_TOKEN,
        }
    ]
    assert result.execution_envelope_id == envelope.execution_envelope_id
    assert result.request_id == REQUEST_ID
    assert result.operation == "github_write"
    assert result.target == GITHUB_TARGET
    assert result.client_response["status"] == "created"
    assert result.client_response["authorization"] == "[REDACTED]"
    assert result.client_response["debug"]["token"] == "[REDACTED]"
    assert MOCK_GITHUB_TOKEN not in repr(result)


def test_github_adapter_can_read_token_from_injected_connection_env() -> None:
    client = MockGitHubAPI()
    adapter = GitHubAdapter(client, env={GITHUB_TOKEN_ENV_VAR: MOCK_GITHUB_TOKEN})
    envelope = approved_envelope()

    result = adapter.write(github_write_request(envelope=envelope), now=NOW)

    assert client.calls[0]["token"] == MOCK_GITHUB_TOKEN
    assert result.client_response["authorization"] == "[REDACTED]"


def test_github_token_env_var_is_owned_by_adapter_not_backend_agents() -> None:
    allowed_owners = {"connection_settings.py", "github_adapter.py"}
    forbidden_refs: list[str] = []

    for module_filename in backend_module_filenames(PROJECT_ROOT):
        if module_filename in allowed_owners:
            continue

        source_path = backend_module_path(module_filename)
        tree = ast.parse(
            read_backend_module_text(module_filename, PROJECT_ROOT),
            filename=str(source_path),
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value == GITHUB_TOKEN_ENV_VAR:
                forbidden_refs.append(f"{source_path}:{node.lineno}")
            elif isinstance(node, ast.Name) and node.id == "GITHUB_TOKEN_ENV_VAR":
                forbidden_refs.append(f"{source_path}:{node.lineno}")

    assert forbidden_refs == []


def test_github_adapter_reads_token_only_after_execution_gate_allows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(GITHUB_TOKEN_ENV_VAR, MOCK_GITHUB_TOKEN)
    client = MockGitHubAPI()
    adapter = GitHubAdapter(client)

    with pytest.raises(GitHubExecutionGateError, match="not valid"):
        adapter.write(github_write_request(envelope=unapproved_github_write_envelope()), now=NOW)

    assert client.calls == []

    monkeypatch.delenv(GITHUB_TOKEN_ENV_VAR)
    with pytest.raises(GitHubAdapterConfigurationError, match=GITHUB_TOKEN_ENV_VAR):
        adapter.write(github_write_request(envelope=approved_envelope()), now=NOW)

    assert client.calls == []


def test_github_adapter_rejects_invalid_envelope_before_token_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(GITHUB_TOKEN_ENV_VAR, raising=False)
    client = MockGitHubAPI()
    adapter = GitHubAdapter(client)

    with pytest.raises(GitHubExecutionGateError, match="not valid"):
        adapter.write(github_write_request(envelope=unapproved_github_write_envelope()), now=NOW)

    assert client.calls == []


@pytest.mark.parametrize(
    ("envelope", "expected_reason"),
    [
        (None, "requires an execution envelope"),
        ({"operation": "github_write"}, "invalid"),
        (unapproved_github_write_envelope(), "not valid"),
        (
            approved_envelope().model_copy(update={"allow": False}),
            "does not allow execution",
        ),
        (approved_envelope(operation="publish"), "operation must be github_write"),
        (
            approved_envelope().model_copy(update={"expires_at": NOW - timedelta(seconds=1)}),
            "expired",
        ),
        (
            approved_envelope().model_copy(update={"signature": ""}),
            "signature",
        ),
        (
            approved_envelope(target="github://artprof964/AI-Art/pulls"),
            "target does not match",
        ),
    ],
)
def test_github_write_rejects_invalid_execution_envelopes_before_client_execution(
    monkeypatch: pytest.MonkeyPatch,
    envelope: object,
    expected_reason: str,
) -> None:
    monkeypatch.setenv(GITHUB_TOKEN_ENV_VAR, MOCK_GITHUB_TOKEN)
    client = MockGitHubAPI()
    adapter = GitHubAdapter(client)

    with pytest.raises(GitHubExecutionGateError, match=expected_reason):
        adapter.write(github_write_request(envelope=envelope), now=NOW)

    assert client.calls == []


@pytest.mark.parametrize(
    ("method", "path", "expected_reason"),
    [
        ("GET", GITHUB_PATH, "only permits write methods"),
        ("POST", "repos/artprof964/AI-Art/issues", "start with /"),
        ("POST", "https://api.github.com/repos/artprof964/AI-Art/issues", "absolute URL"),
        ("POST", "//api.github.com/repos/artprof964/AI-Art/issues", "absolute URL"),
        ("POST", "/repos/artprof964/AI-Art/../issues", "traversal"),
        ("POST", "/repos\\artprof964\\AI-Art\\issues", "forward slashes"),
        ("POST", "/repos/artprof964/AI-Art/issues\n/1", "control characters"),
    ],
)
def test_github_adapter_rejects_unsafe_api_shapes_before_client_execution(
    monkeypatch: pytest.MonkeyPatch,
    method: str,
    path: str,
    expected_reason: str,
) -> None:
    monkeypatch.setenv(GITHUB_TOKEN_ENV_VAR, MOCK_GITHUB_TOKEN)
    client = MockGitHubAPI()
    adapter = GitHubAdapter(client)

    with pytest.raises(GitHubExecutionGateError, match=expected_reason):
        adapter.write(
            GitHubWriteRequest(
                method=method,
                path=path,
                payload={"title": "blocked"},
                target=GITHUB_TARGET,
                execution_envelope=approved_envelope(),
            ),
            now=NOW,
        )

    assert client.calls == []


@pytest.mark.parametrize(
    ("method", "path", "expected_reason"),
    [
        ("POST", "//api.github.com/repos/artprof964/AI-Art/issues", "absolute URL"),
        ("POST", "/repos/artprof964/AI-Art/../issues", "traversal"),
    ],
)
def test_github_adapter_rejects_unsafe_paths_before_token_read(
    monkeypatch: pytest.MonkeyPatch,
    method: str,
    path: str,
    expected_reason: str,
) -> None:
    monkeypatch.delenv(GITHUB_TOKEN_ENV_VAR, raising=False)
    client = MockGitHubAPI()
    adapter = GitHubAdapter(client)

    with pytest.raises(GitHubExecutionGateError, match=expected_reason):
        adapter.write(
            GitHubWriteRequest(
                method=method,
                path=path,
                payload={"title": "blocked"},
                target=GITHUB_TARGET,
                execution_envelope=approved_envelope(),
            ),
            now=NOW,
        )

    assert client.calls == []


def test_github_adapter_uses_shared_url_boundary_directly() -> None:
    source = read_backend_module_text("github_adapter.py", PROJECT_ROOT)

    assert "def _normalize_api_path(" not in source
    assert "safe_relative_api_path(" in source


def test_github_adapter_uses_shared_operation_constant_directly() -> None:
    source = read_backend_module_text("github_adapter.py", PROJECT_ROOT)

    assert "GITHUB_WRITE_OPERATION =" not in source
    assert '"GITHUB_WRITE_OPERATION"' not in source
    assert "operation=OPERATION_GITHUB_WRITE" in source


def test_github_adapter_uses_shared_missing_envelope_message() -> None:
    source = read_backend_module_text("github_adapter.py", PROJECT_ROOT)

    assert '"GitHub write requires an execution envelope"' not in source
    assert "execution_envelope_required(GITHUB_WRITE_ACTION_LABEL)" in source
