from datetime import timedelta
import ast
from uuid import UUID

import pytest

from backend.execution_gate import ExecutionGateError, require_execution_envelope
from backend.execution_gate_messages import (
    EXECUTION_ENVELOPE_EXPIRED,
    EXECUTION_ENVELOPE_INVALID_SIGNATURE,
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
from backend.policy_contracts import (
    LOCAL_ENVELOPE_SIGNING_KEY,
    execution_envelope_signature,
)
from backend.schemas import ExecutionEnvelopeResponse, SourceFreshness
from backend.time_utils import utc_now
from human_approval_helpers import (
    approved_human_approval_for_test,
    unapproved_human_approval_for_test,
)
from path_helpers import read_backend_source, read_test_source


REQUEST_ID = UUID("42424242-4242-4242-4242-424242424242")
ENVELOPE_ID = UUID("43434343-4343-4343-4343-434343434343")
NOW = utc_now()


def envelope(**overrides: object) -> ExecutionEnvelopeResponse:
    base = {
        "execution_envelope_id": ENVELOPE_ID,
        "request_id": REQUEST_ID,
        "operation": "publish",
        "target": "channel:main",
        "allow": True,
        "valid": True,
        "requires_human_approval": True,
        "human_approval": approved_human_approval_for_test(),
        "source_freshness": SourceFreshness(
            all_required_sources_unchanged=True,
            changed_source_count=0,
        ),
        "policy_version": "test-policy",
        "issued_at": NOW,
        "expires_at": NOW + timedelta(minutes=5),
        "signature": "",
        "reason": "approved",
    }
    should_sign = "signature" not in overrides
    base.update(overrides)
    if should_sign:
        base["signature"] = execution_envelope_signature(
            signing_key=LOCAL_ENVELOPE_SIGNING_KEY,
            execution_envelope_id=base["execution_envelope_id"],
            request_id=base["request_id"],
            operation=base["operation"],
            target=base["target"],
            human_approval=base["human_approval"],
            valid=base["valid"],
            allow=base["allow"],
            reason=base["reason"],
            requires_human_approval=base["requires_human_approval"],
            policy_version=base["policy_version"],
            issued_at=base["issued_at"],
            expires_at=base["expires_at"],
        )
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
            envelope(human_approval=unapproved_human_approval_for_test()),
            operation="publish",
            missing_message="missing",
            require_human_approval=True,
            now=NOW,
        )


def test_execution_gate_can_require_human_approval_only_when_marked() -> None:
    require_execution_envelope(
        envelope(
            requires_human_approval=False,
            human_approval=unapproved_human_approval_for_test(),
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
                human_approval=unapproved_human_approval_for_test(),
                operation="github_write",
            ),
            operation="github_write",
            missing_message="missing",
            require_human_approval_when_marked=True,
            now=NOW,
        )


def test_execution_gate_rejects_tampered_signed_envelope() -> None:
    signed_envelope = envelope().model_copy(update={"reason": "tampered reason"})

    with pytest.raises(ExecutionGateError, match="signature is invalid"):
        require_execution_envelope(
            signed_envelope,
            operation="publish",
            missing_message="missing",
            target="channel:main",
            require_human_approval=True,
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
    assert EXECUTION_ENVELOPE_INVALID_SIGNATURE == "execution envelope signature is invalid"
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
    contents = read_backend_source("execution_gate.py")

    forbidden_literals = [
        '"execution envelope is invalid"',
        '"execution envelope is not valid"',
        '"execution envelope does not allow execution"',
        '"execution envelope requires human approval"',
        '"execution envelope must include a signature"',
        '"execution envelope signature is invalid"',
        '"execution envelope is expired"',
        '"execution envelope operation must be',
        '"execution envelope target does not match',
        '" requires human approval"',
    ]
    for literal in forbidden_literals:
        assert literal not in contents
    assert "execution_envelope_operation_mismatch(" in contents
    assert "execution_envelope_target_mismatch(" in contents


def test_envelope_tests_use_shared_human_approval_helper() -> None:
    for test_module in (
        "execution_envelope_helpers.py",
        "test_adapter_results.py",
        "test_execution_gate.py",
        "test_policy_contracts.py",
        "test_publishing_adapter.py",
    ):
        source = read_test_source(test_module)
        tree = ast.parse(source)
        direct_constructor_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "HumanApproval"
        ]

        assert "human_approval_for_test(" in source
        assert direct_constructor_calls == []
