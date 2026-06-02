from __future__ import annotations

import ast
from datetime import timedelta

import pytest

from backend.github_adapter import (
    GITHUB_TOKEN_ENV_VAR,
    GitHubAdapterConfigurationError,
    GitHubExecutionGateError,
)
from backend.repo_paths import (
    backend_module_filenames,
    backend_module_path,
)
from backend.time_utils import utc_now
from connection_env_helpers import TEST_GITHUB_TOKEN, github_token_env
from gated_adapter_helpers import (
    GITHUB_ADAPTER_PATH,
    GITHUB_ADAPTER_REQUEST_ID,
    GITHUB_ADAPTER_TARGET,
    GITHUB_TEST_PAYLOAD,
    approved_github_write_envelope_for_test,
    github_adapter_harness_for_test,
    github_write_request_for_test,
    unapproved_github_write_envelope_for_test,
)
from path_helpers import PROJECT_ROOT, read_backend_source, read_test_source


REQUEST_ID = GITHUB_ADAPTER_REQUEST_ID
NOW = utc_now()
GITHUB_TARGET = GITHUB_ADAPTER_TARGET
GITHUB_PATH = GITHUB_ADAPTER_PATH
MOCK_GITHUB_TOKEN = TEST_GITHUB_TOKEN


def test_github_adapter_uses_mocked_api_and_keeps_token_inside_adapter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(GITHUB_TOKEN_ENV_VAR, MOCK_GITHUB_TOKEN)
    harness = github_adapter_harness_for_test()
    client = harness.client
    adapter = harness.adapter
    envelope = approved_github_write_envelope_for_test(approved_at=NOW)

    result = adapter.write(github_write_request_for_test(execution_envelope=envelope), now=NOW)

    assert client.calls == [
        {
            "method": "POST",
            "path": GITHUB_PATH,
            "json": GITHUB_TEST_PAYLOAD,
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
    harness = github_adapter_harness_for_test(env=github_token_env())
    client = harness.client
    adapter = harness.adapter
    envelope = approved_github_write_envelope_for_test(approved_at=NOW)

    result = adapter.write(github_write_request_for_test(execution_envelope=envelope), now=NOW)

    assert client.calls[0]["token"] == MOCK_GITHUB_TOKEN
    assert result.client_response["authorization"] == "[REDACTED]"


def test_github_adapter_supports_explicit_token_connection_injection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(GITHUB_TOKEN_ENV_VAR, raising=False)
    harness = github_adapter_harness_for_test(token=f"  {MOCK_GITHUB_TOKEN}  ")
    client = harness.client
    adapter = harness.adapter
    envelope = approved_github_write_envelope_for_test(approved_at=NOW)

    result = adapter.write(github_write_request_for_test(execution_envelope=envelope), now=NOW)

    assert client.calls[0]["token"] == MOCK_GITHUB_TOKEN
    assert result.client_response["debug"]["token"] == "[REDACTED]"
    assert MOCK_GITHUB_TOKEN not in repr(result)


def test_github_token_env_var_is_owned_by_adapter_not_backend_agents() -> None:
    allowed_owners = {
        "adapter_factory.py",
        "connection_settings.py",
        "github_adapter.py",
    }
    forbidden_refs: list[str] = []

    for module_filename in backend_module_filenames(PROJECT_ROOT):
        if module_filename in allowed_owners:
            continue

        source_path = backend_module_path(module_filename)
        tree = ast.parse(
            read_backend_source(module_filename),
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
    harness = github_adapter_harness_for_test()
    client = harness.client
    adapter = harness.adapter

    with pytest.raises(GitHubExecutionGateError, match="not valid"):
        adapter.write(
            github_write_request_for_test(
                execution_envelope=unapproved_github_write_envelope_for_test()
            ),
            now=NOW,
        )

    assert client.calls == []

    monkeypatch.delenv(GITHUB_TOKEN_ENV_VAR)
    with pytest.raises(GitHubAdapterConfigurationError, match=GITHUB_TOKEN_ENV_VAR):
        adapter.write(
            github_write_request_for_test(
                execution_envelope=approved_github_write_envelope_for_test(approved_at=NOW)
            ),
            now=NOW,
        )

    assert client.calls == []


def test_github_adapter_rejects_invalid_envelope_before_token_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(GITHUB_TOKEN_ENV_VAR, raising=False)
    harness = github_adapter_harness_for_test()
    client = harness.client
    adapter = harness.adapter

    with pytest.raises(GitHubExecutionGateError, match="not valid"):
        adapter.write(
            github_write_request_for_test(
                execution_envelope=unapproved_github_write_envelope_for_test()
            ),
            now=NOW,
        )

    assert client.calls == []


@pytest.mark.parametrize(
    ("envelope", "expected_reason"),
    [
        (None, "requires an execution envelope"),
        ({"operation": "github_write"}, "invalid"),
        (unapproved_github_write_envelope_for_test(), "not valid"),
        (
            approved_github_write_envelope_for_test(approved_at=NOW).model_copy(
                update={"allow": False}
            ),
            "does not allow execution",
        ),
        (
            approved_github_write_envelope_for_test(operation="publish", approved_at=NOW),
            "operation must be github_write",
        ),
        (
            approved_github_write_envelope_for_test(approved_at=NOW).model_copy(
                update={"expires_at": NOW - timedelta(seconds=1)}
            ),
            "expired",
        ),
        (
            approved_github_write_envelope_for_test(approved_at=NOW).model_copy(
                update={"signature": ""}
            ),
            "signature",
        ),
        (
            approved_github_write_envelope_for_test(
                target="github://artprof964/AI-Art/pulls",
                approved_at=NOW,
            ),
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
    harness = github_adapter_harness_for_test()
    client = harness.client
    adapter = harness.adapter

    with pytest.raises(GitHubExecutionGateError, match=expected_reason):
        adapter.write(github_write_request_for_test(execution_envelope=envelope), now=NOW)

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
    harness = github_adapter_harness_for_test()
    client = harness.client
    adapter = harness.adapter

    with pytest.raises(GitHubExecutionGateError, match=expected_reason):
        adapter.write(
            github_write_request_for_test(
                method=method,
                path=path,
                payload={"title": "blocked"},
                target=GITHUB_TARGET,
                execution_envelope=approved_github_write_envelope_for_test(approved_at=NOW),
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
    harness = github_adapter_harness_for_test()
    client = harness.client
    adapter = harness.adapter

    with pytest.raises(GitHubExecutionGateError, match=expected_reason):
        adapter.write(
            github_write_request_for_test(
                method=method,
                path=path,
                payload={"title": "blocked"},
                target=GITHUB_TARGET,
                execution_envelope=approved_github_write_envelope_for_test(approved_at=NOW),
            ),
            now=NOW,
        )

    assert client.calls == []


def test_github_adapter_uses_shared_url_boundary_directly() -> None:
    source = read_backend_source("github_adapter.py")

    assert "def _normalize_api_path(" not in source
    assert "safe_relative_api_path(" in source


def test_github_adapter_uses_shared_runtime_secret_resolver() -> None:
    source = read_backend_source("github_adapter.py")

    assert "adapter_runtime_secret(" in source
    assert "explicit_secret=self._token" in source
    assert 'setting_name="github_token"' not in source
    assert "require_runtime_secret(" not in source
    assert "load_connection_settings(" not in source
    assert "require_env_value(" not in source
    assert "runtime_env(" not in source
    assert "github_token_required(" not in source
    assert "def _read_runtime_token(" not in source


def test_github_adapter_uses_shared_operation_constant_directly() -> None:
    source = read_backend_source("github_adapter.py")

    assert "GITHUB_WRITE_OPERATION =" not in source
    assert '"GITHUB_WRITE_OPERATION"' not in source
    assert "operation=OPERATION_GITHUB_WRITE" in source


def test_github_adapter_uses_shared_missing_envelope_message() -> None:
    source = read_backend_source("github_adapter.py")

    assert '"GitHub write requires an execution envelope"' not in source
    assert "execution_envelope_required(GITHUB_WRITE_ACTION_LABEL)" in source


def test_github_adapter_tests_use_shared_execution_envelope_helper() -> None:
    source = read_test_source("test_github_adapter.py")
    tree = ast.parse(source)
    function_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    class_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    imported_names = {
        (node.module, alias.name)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    direct_adapter_calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "GitHubAdapter"
    }

    assert "approved_github_write_envelope_for_test" in called_names
    assert "unapproved_github_write_envelope_for_test" in called_names
    assert "github_write_request_for_test" in called_names
    assert "github_adapter_harness_for_test" in called_names
    assert "approved_execution_envelope" not in called_names
    assert "unapproved_execution_envelope" not in called_names
    assert "approved_envelope" not in function_names
    assert "unapproved_github_write_envelope" not in function_names
    assert "github_write_request" not in function_names
    assert "MockGitHubAPI" not in class_names
    assert "GitHubAdapterHarness" not in class_names
    assert not direct_adapter_calls
    assert ("backend.github_adapter", "GitHubAdapter") not in imported_names
    assert ("backend.github_adapter", "GitHubWriteRequest") not in imported_names
    assert ("backend.schemas", "ExecutionEnvelopeRequest") not in imported_names
    assert ("backend.service", "create_execution_envelope") not in imported_names
