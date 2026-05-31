import json
from typing import Any

import pytest

from backend.canonical_hash import canonical_json
from backend.repo_paths import OPA_POLICY_PATH, repo_path
from backend.shell_commands import (
    docker_compose_exec_args,
    missing_command_result,
    run_process,
    shell_args,
)
from path_helpers import PROJECT_ROOT

OPA_POLICY = repo_path(PROJECT_ROOT, OPA_POLICY_PATH)
_OPA_COMMAND: list[str] | None = None
_OPA_SKIP_REASON: str | None = None


def opa_eval(query: str, input_data: dict[str, Any]) -> Any:
    result = _run_opa_eval(input_data=input_data, query=query)

    body = json.loads(result.stdout)
    return body["result"][0]["expressions"][0]["value"]


def _run_opa_eval(*, input_data: dict[str, Any], query: str) -> Any:
    command = _opa_command()
    return run_process(
        [*command, query],
        input=canonical_json(input_data),
        check=True,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )


def _opa_command() -> list[str]:
    global _OPA_COMMAND, _OPA_SKIP_REASON

    if _OPA_COMMAND is not None:
        return _OPA_COMMAND
    if _OPA_SKIP_REASON is not None:
        pytest.skip(_OPA_SKIP_REASON)

    candidates = [
        (
            docker_compose_exec_args(
                "opa",
                "/opa",
                "eval",
                "--format",
                "json",
                "--data",
                "/policies/ai_artist.rego",
                "--stdin-input",
            ),
            "running docker compose opa service",
        ),
        (
            shell_args(
                "opa",
                "eval",
                "--format",
                "json",
                "--data",
                str(OPA_POLICY),
                "--stdin-input",
            ),
            "local opa CLI",
        ),
    ]

    errors: list[str] = []
    for command, label in candidates:
        probe = _probe_opa_command(command)
        if probe.returncode == 0:
            _OPA_COMMAND = command
            return command
        errors.append(f"{label}: {_compact_error(probe)}")

    _OPA_SKIP_REASON = (
        "OPA policy tests require a running docker compose opa service or local opa CLI; "
        f"checked {', '.join(errors)}"
    )
    pytest.skip(_OPA_SKIP_REASON)


def _probe_opa_command(command: list[str]) -> Any:
    try:
        return run_process(
            [*command, "true"],
            input="{}",
            check=False,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
    except FileNotFoundError as exc:
        return missing_command_result(command, exc)


def _compact_error(result: Any) -> str:
    output = (result.stderr or result.stdout).strip().splitlines()
    if not output:
        return f"exit {result.returncode}"
    return output[-1]


def policy_input(
    operation: str,
    *,
    request_kind: str = "action",
    source_freshness: dict[str, Any] | None = None,
    execution_envelope: dict[str, Any] | None = None,
    human_approval: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "request_kind": request_kind,
        "operation": operation,
        "source_freshness": source_freshness or {},
        "execution_envelope": execution_envelope or {},
        "human_approval": human_approval or {},
    }


def valid_envelope(operation: str) -> dict[str, Any]:
    return {"valid": True, "operation": operation}


def valid_human_approval() -> dict[str, Any]:
    return {"approved": True, "approver_scope": "user:owner"}


def assert_allowed(input_data: dict[str, Any]) -> None:
    assert opa_eval("data.ai_artist.allow", input_data) is True


def assert_denied_by_default(input_data: dict[str, Any]) -> None:
    assert opa_eval("data.ai_artist.allow", input_data) is False
    assert (
        opa_eval("data.ai_artist.deny_reason", input_data)
        == "operation denied by default policy"
    )


def test_unknown_action_is_denied_by_default() -> None:
    assert_denied_by_default(policy_input("unknown"))
    assert_denied_by_default(
        policy_input(
            "unknown",
            execution_envelope=valid_envelope("unknown"),
            human_approval=valid_human_approval(),
        ),
    )


def test_read_is_allowed_only_for_read_request_kind() -> None:
    assert_allowed(policy_input("read", request_kind="read"))

    for request_kind in ["action", "mixed", ""]:
        assert_denied_by_default(policy_input("read", request_kind=request_kind))


def test_cache_replay_requires_read_kind_unchanged_required_sources_and_zero_changes() -> None:
    fresh_reuse = policy_input(
        "reuse",
        request_kind="read",
        source_freshness={
            "all_required_sources_unchanged": True,
            "changed_source_count": 0,
        },
    )
    changed_sources = policy_input(
        "reuse",
        request_kind="read",
        source_freshness={
            "all_required_sources_unchanged": True,
            "changed_source_count": 1,
        },
    )
    changed_required_sources = policy_input(
        "reuse",
        request_kind="read",
        source_freshness={
            "all_required_sources_unchanged": False,
            "changed_source_count": 0,
        },
    )
    action_reuse = policy_input(
        "reuse",
        request_kind="action",
        source_freshness={
            "all_required_sources_unchanged": True,
            "changed_source_count": 0,
        },
    )

    assert_allowed(fresh_reuse)
    assert_denied_by_default(changed_sources)
    assert_denied_by_default(changed_required_sources)
    assert_denied_by_default(action_reuse)


@pytest.mark.parametrize("operation", ["write", "publish", "delete", "github_write"])
def test_write_operations_are_denied_without_valid_envelope_and_approval(operation: str) -> None:
    assert_denied_by_default(policy_input(operation))
    assert_denied_by_default(
        policy_input(
            operation,
            execution_envelope=valid_envelope(operation),
        ),
    )
    assert_denied_by_default(
        policy_input(
            operation,
            human_approval=valid_human_approval(),
        ),
    )
    assert_denied_by_default(
        policy_input(
            operation,
            execution_envelope=valid_envelope(operation),
            human_approval={"approved": False, "approver_scope": "user:owner"},
        ),
    )
    assert opa_eval("data.ai_artist.requires_human_approval", policy_input(operation)) is True


@pytest.mark.parametrize("operation", ["write", "publish", "delete", "github_write"])
def test_write_operations_allow_valid_envelope_with_human_scope(operation: str) -> None:
    approved_input = policy_input(
        operation,
        execution_envelope=valid_envelope(operation),
        human_approval=valid_human_approval(),
    )
    missing_approver_input = policy_input(
        operation,
        execution_envelope=valid_envelope(operation),
        human_approval={"approved": True},
    )
    mismatched_envelope_input = policy_input(
        operation,
        execution_envelope=valid_envelope("read"),
        human_approval=valid_human_approval(),
    )
    invalid_envelope_input = policy_input(
        operation,
        execution_envelope={"valid": False, "operation": operation},
        human_approval=valid_human_approval(),
    )

    assert_allowed(approved_input)
    assert_denied_by_default(missing_approver_input)
    assert_denied_by_default(mismatched_envelope_input)
    assert_denied_by_default(invalid_envelope_input)


def test_image_generation_requires_valid_matching_execution_envelope() -> None:
    assert_denied_by_default(policy_input("image_generate"))
    assert_denied_by_default(
        policy_input(
            "image_generate",
            execution_envelope=valid_envelope("publish"),
        ),
    )
    assert_allowed(
        policy_input(
            "image_generate",
            execution_envelope=valid_envelope("image_generate"),
        ),
    )
    assert (
        opa_eval(
            "data.ai_artist.requires_human_approval",
            {**policy_input("image_generate"), "review_required": True},
        )
        is True
    )
