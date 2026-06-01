import ast
from datetime import timedelta

import pytest

from backend.adapter_gate_contracts import COMFYUI_IMAGE_GENERATION_ACTION_LABEL
from backend.comfyui_adapter import (
    ComfyUIExecutionGateError,
)
from backend.time_utils import utc_now
from gated_adapter_helpers import (
    COMFYUI_ADAPTER_REQUEST_ID,
    COMFYUI_ADAPTER_TARGET,
    COMFYUI_TEST_PROMPT_ID,
    COMFYUI_TEST_WORKFLOW,
    approved_comfyui_envelope_for_test,
    comfyui_adapter_harness_for_test,
    comfyui_image_request_for_test,
    unapproved_comfyui_envelope_for_test,
)
from path_helpers import read_backend_source, read_test_source


REQUEST_ID = COMFYUI_ADAPTER_REQUEST_ID
NOW = utc_now()
COMFYUI_TARGET = COMFYUI_ADAPTER_TARGET


def test_image_generation_succeeds_with_mocked_approved_execution_envelope() -> None:
    harness = comfyui_adapter_harness_for_test()
    client = harness.client
    adapter = harness.adapter
    envelope = approved_comfyui_envelope_for_test(approved_at=NOW)
    workflow = dict(COMFYUI_TEST_WORKFLOW)

    result = adapter.generate_image(
        comfyui_image_request_for_test(
            execution_envelope=envelope,
            workflow=workflow,
        ),
        now=NOW,
    )

    assert client.calls == [workflow]
    assert result.execution_envelope_id == envelope.execution_envelope_id
    assert result.request_id == REQUEST_ID
    assert result.operation == "image_generate"
    assert result.client_response["prompt_id"] == COMFYUI_TEST_PROMPT_ID


@pytest.mark.parametrize(
    ("envelope", "expected_reason"),
    [
        (None, "requires an execution envelope"),
        ({"operation": "image_generate"}, "invalid"),
        (unapproved_comfyui_envelope_for_test(), "not valid"),
        (
            approved_comfyui_envelope_for_test(approved_at=NOW).model_copy(update={"allow": False}),
            "does not allow execution",
        ),
        (
            approved_comfyui_envelope_for_test(operation="publish", approved_at=NOW),
            "operation must be image_generate",
        ),
        (
            approved_comfyui_envelope_for_test(approved_at=NOW).model_copy(
                update={"expires_at": NOW - timedelta(seconds=1)}
            ),
            "expired",
        ),
        (
            approved_comfyui_envelope_for_test(approved_at=NOW).model_copy(update={"signature": ""}),
            "signature",
        ),
    ],
)
def test_image_generation_fails_without_valid_execution_envelope(
    envelope: object,
    expected_reason: str,
) -> None:
    harness = comfyui_adapter_harness_for_test()
    client = harness.client
    adapter = harness.adapter

    with pytest.raises(ComfyUIExecutionGateError, match=expected_reason):
        adapter.generate_image(
            comfyui_image_request_for_test(
                workflow={"nodes": []},
                execution_envelope=envelope,
            ),
            now=NOW,
        )

    assert client.calls == []


def test_comfyui_adapter_uses_shared_operation_constant_directly() -> None:
    contents = read_backend_source("comfyui_adapter.py")

    assert "IMAGE_GENERATE_OPERATION =" not in contents
    assert "operation=OPERATION_IMAGE_GENERATE" in contents


def test_comfyui_adapter_uses_shared_missing_envelope_message() -> None:
    contents = read_backend_source("comfyui_adapter.py")

    assert '"image generation requires an execution envelope"' not in contents
    assert 'execution_envelope_required("image generation")' not in contents
    assert "execution_envelope_required(COMFYUI_IMAGE_GENERATION_ACTION_LABEL)" in contents


def test_comfyui_adapter_gate_labels_are_centralized() -> None:
    assert COMFYUI_IMAGE_GENERATION_ACTION_LABEL == "image generation"

    contents = read_backend_source("comfyui_adapter.py")
    assert '"image generation"' not in contents
    assert "COMFYUI_IMAGE_GENERATION_ACTION_LABEL" in contents


def test_comfyui_adapter_tests_use_shared_execution_envelope_helper() -> None:
    contents = read_test_source("test_comfyui_adapter.py")
    tree = ast.parse(contents)
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
        and node.func.id == "ComfyUIAdapter"
    }

    assert "approved_comfyui_envelope_for_test" in called_names
    assert "unapproved_comfyui_envelope_for_test" in called_names
    assert "comfyui_image_request_for_test" in called_names
    assert "comfyui_adapter_harness_for_test" in called_names
    assert "approved_execution_envelope" not in called_names
    assert "unapproved_execution_envelope" not in called_names
    assert "approved_envelope" not in function_names
    assert "unapproved_envelope" not in function_names
    assert "MockComfyUIClient" not in class_names
    assert "ComfyUIAdapterHarness" not in class_names
    assert not direct_adapter_calls
    assert ("backend.comfyui_adapter", "ComfyUIAdapter") not in imported_names
    assert ("backend.comfyui_adapter", "ComfyUIImageGenerationRequest") not in imported_names
    assert ("backend.schemas", "ExecutionEnvelopeRequest") not in imported_names
    assert ("backend.service", "create_execution_envelope") not in imported_names
