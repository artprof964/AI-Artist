from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from backend.execution_gate import ExecutionGateError, require_execution_envelope
from backend.execution_gate_messages import (
    EXECUTION_ENVELOPE_EXPIRED,
    EXECUTION_ENVELOPE_INVALID,
    EXECUTION_ENVELOPE_MISSING_SIGNATURE,
    EXECUTION_ENVELOPE_NOT_ALLOWED,
    EXECUTION_ENVELOPE_NOT_VALID,
    EXECUTION_ENVELOPE_REQUIRES_HUMAN_APPROVAL,
    execution_envelope_required,
    execution_envelope_operation_mismatch,
    execution_envelope_target_mismatch,
    operation_requires_human_approval,
)
from backend.repo_paths import read_backend_module_text
from backend.schemas import ExecutionEnvelopeResponse, HumanApproval, SourceFreshness


REQUEST_ID = UUID("42424242-4242-4242-4242-424242424242")
ENVELOPE_ID = UUID("43434343-4343-4343-4343-434343434343")
NOW = datetime.now(timezone.utc)


def envelope(**overrides: object) -> ExecutionEnvelopeResponse:
    base = {
        "execution_envelope_id": ENVELOPE_ID,
        "request_id": REQUEST_ID,
        "operation": "publish",
        "target": "channel:main",
        "allow": True,
        "valid": True,
        "requires_human_approval": True,
        "human_approval": HumanApproval(approved=True, approver="tester"),
        "source_freshness": SourceFreshness(
            all_required_sources_unchanged=True,
            changed_source_count=0,
        ),
        "policy_version": "test-policy",
        "issued_at": NOW,
        "expires_at": NOW + timedelta(minutes=5),
        "signature": "hmac-sha256:signature",
        "reason": "approved",
    }
    base.update(overrides)
    return ExecutionEnvelopeResponse.model_validate(base)


def test_execution_gate_accepts_model_or_dict_envelopes() -> None:
    model_result = require_execution_envelope(
        envelope(),
        operation="publish",
        missing_message="missing",
        target="channel:main",
        require_human_approval=True,
        now=NOW,
    )
    dict_result = require_execution_envelope(
        envelope().model_dump(mode="json"),
        operation="publish",
        missing_message="missing",
        target="channel:main",
        require_human_approval=True,
        now=NOW,
    )

    assert model_result.request_id == REQUEST_ID
    assert dict_result.request_id == REQUEST_ID


@pytest.mark.parametrize(
    ("candidate", "match"),
    [
        (None, "missing envelope"),
        ({"not": "an envelope"}, "invalid"),
        (envelope(operation="github_write"), "operation must be publish"),
        (envelope(target="channel:other"), "target does not match publish target"),
        (envelope(valid=False), "not valid"),
        (envelope(allow=False), "does not allow"),
        (envelope(signature=""), "signature"),
        (envelope(expires_at=NOW - timedelta(seconds=1)), "expired"),
    ],
)
def test_execution_gate_rejects_invalid_envelopes(candidate: object, match: str) -> None:
    with pytest.raises(ExecutionGateError, match=match):
        require_execution_envelope(
            candidate,
            operation="publish",
            missing_message="missing envelope",
            target="channel:main",
            target_label="publish target",
            now=NOW,
        )


def test_execution_gate_can_require_human_approval_unconditionally() -> None:
    with pytest.raises(ExecutionGateError, match="publish requires human approval"):
        require_execution_envelope(
            envelope(human_approval=HumanApproval(approved=False)),
            operation="publish",
            missing_message="missing",
            require_human_approval=True,
            now=NOW,
        )


def test_execution_gate_can_require_human_approval_only_when_marked() -> None:
    require_execution_envelope(
        envelope(
            requires_human_approval=False,
            human_approval=HumanApproval(approved=False),
            operation="github_write",
        ),
        operation="github_write",
        missing_message="missing",
        require_human_approval_when_marked=True,
        now=NOW,
    )

    with pytest.raises(ExecutionGateError, match="requires human approval"):
        require_execution_envelope(
            envelope(
                requires_human_approval=True,
                human_approval=HumanApproval(approved=False),
                operation="github_write",
            ),
            operation="github_write",
            missing_message="missing",
            require_human_approval_when_marked=True,
            now=NOW,
        )


def test_execution_gate_error_message_contracts_are_shared() -> None:
    assert EXECUTION_ENVELOPE_INVALID == "execution envelope is invalid"
    assert EXECUTION_ENVELOPE_NOT_VALID == "execution envelope is not valid"
    assert EXECUTION_ENVELOPE_NOT_ALLOWED == "execution envelope does not allow execution"
    assert (
        EXECUTION_ENVELOPE_REQUIRES_HUMAN_APPROVAL
        == "execution envelope requires human approval"
    )
    assert EXECUTION_ENVELOPE_MISSING_SIGNATURE == "execution envelope must include a signature"
    assert EXECUTION_ENVELOPE_EXPIRED == "execution envelope is expired"
    assert (
        execution_envelope_operation_mismatch("publish")
        == "execution envelope operation must be publish"
    )
    assert (
        execution_envelope_target_mismatch("publish target")
        == "execution envelope target does not match publish target"
    )
    assert execution_envelope_required("publishing") == "publishing requires an execution envelope"
    assert operation_requires_human_approval("publish") == "publish requires human approval"


def test_execution_gate_uses_shared_error_message_contracts() -> None:
    contents = read_backend_module_text("execution_gate.py")

    forbidden_literals = [
        '"execution envelope is invalid"',
        '"execution envelope is not valid"',
        '"execution envelope does not allow execution"',
        '"execution envelope requires human approval"',
        '"execution envelope must include a signature"',
        '"execution envelope is expired"',
        '"execution envelope operation must be',
        '"execution envelope target does not match',
        '" requires human approval"',
    ]
    for literal in forbidden_literals:
        assert literal not in contents
    assert "execution_envelope_operation_mismatch(" in contents
    assert "execution_envelope_target_mismatch(" in contents
