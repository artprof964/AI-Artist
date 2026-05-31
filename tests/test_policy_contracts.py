from uuid import UUID

from backend.policy_contracts import LOCAL_DEFAULT_DENY_POLICY_VERSION
from backend.schemas import ExecutionEnvelopeRequest, PolicyEvaluateRequest
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
