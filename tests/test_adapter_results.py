from datetime import timedelta
from uuid import UUID

from backend.adapter_results import (
    ADAPTER_RESULT_CLIENT_RESPONSE_FIELD,
    ADAPTER_RESULT_EXECUTION_ENVELOPE_ID_FIELD,
    ADAPTER_RESULT_OPERATION_FIELD,
    ADAPTER_RESULT_REQUEST_ID_FIELD,
    ADAPTER_RESULT_TARGET_FIELD,
    gated_result_fields,
    targeted_result_fields,
)
from backend.runtime_field_contracts import (
    CLIENT_RESPONSE_FIELD,
    EXECUTION_ENVELOPE_ID_FIELD,
    OPERATION_FIELD,
    REQUEST_ID_FIELD,
    TARGET_FIELD,
)
from backend.schemas import ExecutionEnvelopeResponse, HumanApproval, SourceFreshness
from backend.time_utils import utc_now
from path_helpers import read_backend_source


REQUEST_ID = UUID("53535353-5353-5353-5353-535353535353")
ENVELOPE_ID = UUID("54545454-5454-5454-5454-545454545454")
NOW = utc_now()


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


def test_adapter_result_field_vocabulary_is_centralized() -> None:
    assert ADAPTER_RESULT_EXECUTION_ENVELOPE_ID_FIELD == EXECUTION_ENVELOPE_ID_FIELD
    assert ADAPTER_RESULT_REQUEST_ID_FIELD == REQUEST_ID_FIELD
    assert ADAPTER_RESULT_OPERATION_FIELD == OPERATION_FIELD
    assert ADAPTER_RESULT_TARGET_FIELD == TARGET_FIELD
    assert ADAPTER_RESULT_CLIENT_RESPONSE_FIELD == CLIENT_RESPONSE_FIELD


def test_adapter_result_contracts_use_runtime_field_names() -> None:
    source = read_backend_source("adapter_results.py")

    assert "ADAPTER_RESULT_EXECUTION_ENVELOPE_ID_FIELD = EXECUTION_ENVELOPE_ID_FIELD" in source
    assert "ADAPTER_RESULT_REQUEST_ID_FIELD = REQUEST_ID_FIELD" in source
    assert "ADAPTER_RESULT_OPERATION_FIELD = OPERATION_FIELD" in source
    assert "ADAPTER_RESULT_TARGET_FIELD = TARGET_FIELD" in source
    assert "ADAPTER_RESULT_CLIENT_RESPONSE_FIELD = CLIENT_RESPONSE_FIELD" in source
    assert 'ADAPTER_RESULT_EXECUTION_ENVELOPE_ID_FIELD = "execution_envelope_id"' not in source
    assert 'ADAPTER_RESULT_REQUEST_ID_FIELD = "request_id"' not in source
    assert 'ADAPTER_RESULT_OPERATION_FIELD = "operation"' not in source
    assert 'ADAPTER_RESULT_TARGET_FIELD = "target"' not in source
    assert 'ADAPTER_RESULT_CLIENT_RESPONSE_FIELD = "client_response"' not in source
