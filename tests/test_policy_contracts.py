from datetime import datetime, timezone
from uuid import UUID

from backend.policy_contracts import (
    EXECUTION_ENVELOPE_SIGNATURE_PREFIX,
    EXECUTION_ENVELOPE_TTL_MINUTES,
    LOCAL_DEFAULT_DENY_POLICY_VERSION,
    LOCAL_ENVELOPE_SIGNING_KEY,
    execution_envelope_expires_at,
    execution_envelope_signature,
    execution_envelope_signature_is_valid,
)
from backend.schemas import ExecutionEnvelopeRequest, HumanApproval, PolicyEvaluateRequest
from backend.service import create_execution_envelope, evaluate_policy
from path_helpers import read_backend_source


def test_policy_version_contract_is_shared_by_policy_and_envelope_responses() -> None:
    policy_response = evaluate_policy(
        PolicyEvaluateRequest(
            request_kind="read",
            operation="read",
            requester_scope="user:local",
            policy_scope="workspace:ai-artist-main",
            requires_human_approval=False,
        )
    )
    envelope_response = create_execution_envelope(
        ExecutionEnvelopeRequest(
            request_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            request_kind="read",
            operation="read",
            requester_scope="user:local",
            policy_scope="workspace:ai-artist-main",
            target="knowledge://local",
        )
    )

    assert policy_response.policy_version == LOCAL_DEFAULT_DENY_POLICY_VERSION
    assert envelope_response.policy_version == LOCAL_DEFAULT_DENY_POLICY_VERSION


def test_service_uses_shared_policy_version_contract() -> None:
    service_source = read_backend_source("service.py")
    contract_source = read_backend_source("policy_contracts.py")

    assert "LOCAL_DEFAULT_DENY_POLICY_VERSION" in service_source
    assert 'POLICY_VERSION = "local-default-deny-v0"' not in service_source
    assert '"local-default-deny-v0"' not in service_source
    assert 'LOCAL_DEFAULT_DENY_POLICY_VERSION = "local-default-deny-v0"' in contract_source


def test_execution_envelope_signing_and_ttl_contracts_are_shared() -> None:
    issued_at = datetime(2026, 5, 31, 10, 0, tzinfo=timezone.utc)

    assert LOCAL_ENVELOPE_SIGNING_KEY == b"ai-artist-local-safety-service-dev-key"
    assert EXECUTION_ENVELOPE_TTL_MINUTES == 15
    assert EXECUTION_ENVELOPE_SIGNATURE_PREFIX == "hmac-sha256:"
    assert execution_envelope_expires_at(issued_at) == datetime(
        2026, 5, 31, 10, 15, tzinfo=timezone.utc
    )


def test_execution_envelope_signature_contract_covers_envelope_fields() -> None:
    issued_at = datetime(2026, 5, 31, 10, 0, tzinfo=timezone.utc)
    expires_at = execution_envelope_expires_at(issued_at)
    human_approval = HumanApproval(
        approved=True,
        approver_scope="user:owner",
        approved_at=issued_at,
    )

    signature = execution_envelope_signature(
        signing_key=LOCAL_ENVELOPE_SIGNING_KEY,
        execution_envelope_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        request_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        operation="publish",
        target="slack://workspace/channel",
        human_approval=human_approval,
        valid=True,
        allow=True,
        reason="publish approved with execution envelope",
        requires_human_approval=True,
        policy_version=LOCAL_DEFAULT_DENY_POLICY_VERSION,
        issued_at=issued_at,
        expires_at=expires_at,
    )

    assert signature.startswith(EXECUTION_ENVELOPE_SIGNATURE_PREFIX)
    assert signature == execution_envelope_signature(
        signing_key=LOCAL_ENVELOPE_SIGNING_KEY,
        execution_envelope_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        request_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        operation="publish",
        target="slack://workspace/channel",
        human_approval=human_approval,
        valid=True,
        allow=True,
        reason="publish approved with execution envelope",
        requires_human_approval=True,
        policy_version=LOCAL_DEFAULT_DENY_POLICY_VERSION,
        issued_at=issued_at,
        expires_at=expires_at,
    )
    assert signature != execution_envelope_signature(
        signing_key=LOCAL_ENVELOPE_SIGNING_KEY,
        execution_envelope_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        request_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        operation="publish",
        target="slack://workspace/channel",
        human_approval=human_approval,
        valid=True,
        allow=True,
        reason="tampered reason",
        requires_human_approval=True,
        policy_version=LOCAL_DEFAULT_DENY_POLICY_VERSION,
        issued_at=issued_at,
        expires_at=expires_at,
    )


def test_created_execution_envelope_signature_verifies_through_shared_contract() -> None:
    envelope = create_execution_envelope(
        ExecutionEnvelopeRequest(
            request_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            request_kind="action",
            operation="publish",
            requester_scope="user:local",
            policy_scope="workspace:ai-artist-main",
            target="slack://workspace/channel",
            human_approval=HumanApproval(approved=True, approver_scope="user:owner"),
        )
    )

    assert execution_envelope_signature_is_valid(
        envelope,
        signing_key=LOCAL_ENVELOPE_SIGNING_KEY,
    )
    assert not execution_envelope_signature_is_valid(
        envelope.model_copy(update={"reason": "tampered"}),
        signing_key=LOCAL_ENVELOPE_SIGNING_KEY,
    )


def test_service_uses_shared_envelope_signing_and_ttl_contracts() -> None:
    service_source = read_backend_source("service.py")
    contract_source = read_backend_source("policy_contracts.py")

    assert "LOCAL_ENVELOPE_SIGNING_KEY" in service_source
    assert "execution_envelope_expires_at(" in service_source
    assert "execution_envelope_signature(" in service_source
    assert "timedelta(minutes=15)" not in service_source
    assert "ai-artist-local-safety-service-dev-key" not in service_source
    assert "signature_payload =" not in service_source
    assert "hmac_sha256_json" not in service_source
    assert "LOCAL_ENVELOPE_SIGNING_KEY = b" in contract_source
    assert "EXECUTION_ENVELOPE_TTL_MINUTES = 15" in contract_source
