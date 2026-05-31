from datetime import datetime, timedelta, timezone
from uuid import UUID

from backend.adapter_results import gated_result_fields, targeted_result_fields
from backend.schemas import ExecutionEnvelopeResponse, HumanApproval, SourceFreshness


REQUEST_ID = UUID("53535353-5353-5353-5353-535353535353")
ENVELOPE_ID = UUID("54545454-5454-5454-5454-545454545454")
NOW = datetime.now(timezone.utc)


def envelope() -> ExecutionEnvelopeResponse:
    return ExecutionEnvelopeResponse(
        execution_envelope_id=ENVELOPE_ID,
        request_id=REQUEST_ID,
        operation="publish",
        target="channel:main",
        human_approval=HumanApproval(approved=True),
        valid=True,
        allow=True,
        reason="approved",
        requires_human_approval=True,
        policy_version="test-policy",
        issued_at=NOW,
        expires_at=NOW + timedelta(minutes=5),
        signature="hmac-sha256:signature",
        source_freshness=SourceFreshness(),
    )


def test_gated_result_fields_map_common_envelope_values() -> None:
    fields = gated_result_fields(
        envelope=envelope(),
        client_response={"status": "ok"},
    )

    assert fields.execution_envelope_id == ENVELOPE_ID
    assert fields.request_id == REQUEST_ID
    assert fields.operation == "publish"
    assert fields.client_response == {"status": "ok"}


def test_targeted_result_fields_add_target_to_common_fields() -> None:
    fields = targeted_result_fields(
        envelope=envelope(),
        target="channel:main",
        client_response={"status": "published"},
    )

    assert fields.execution_envelope_id == ENVELOPE_ID
    assert fields.request_id == REQUEST_ID
    assert fields.operation == "publish"
    assert fields.target == "channel:main"
    assert fields.client_response == {"status": "published"}
