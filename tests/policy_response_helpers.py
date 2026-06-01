from backend.schemas import PolicyEvaluateResponse

DEFAULT_TEST_POLICY_RESPONSE_REASON = "cache replay allowed by OPA"
DEFAULT_TEST_POLICY_VERSION = "test-policy-v1"


def approved_policy_response_for_test(
    *,
    reason: str = DEFAULT_TEST_POLICY_RESPONSE_REASON,
    requires_human_approval: bool = False,
    policy_version: str = DEFAULT_TEST_POLICY_VERSION,
) -> PolicyEvaluateResponse:
    return PolicyEvaluateResponse(
        allow=True,
        reason=reason,
        requires_human_approval=requires_human_approval,
        policy_version=policy_version,
    )
