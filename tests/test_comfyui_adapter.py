import ast
from datetime import timedelta
from typing import Any
from uuid import UUID

import pytest

from backend.adapter_gate_contracts import COMFYUI_IMAGE_GENERATION_ACTION_LABEL
from backend.comfyui_adapter import (
    ComfyUIAdapter,
    ComfyUIExecutionGateError,
    ComfyUIImageGenerationRequest,
)
from backend.time_utils import utc_now
from execution_envelope_helpers import (
    approved_execution_envelope,
    unapproved_execution_envelope,
)
from path_helpers import read_backend_source, read_test_source


REQUEST_ID = UUID("17171717-1717-1717-1717-171717171717")
NOW = utc_now()
COMFYUI_TARGET = "comfyui://workflow/mock-image-generation"


class MockComfyUIClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def submit_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(workflow)
        return {
            "prompt_id": "mock-prompt-001",
            "images": [
                {
                    "filename": "mock-image.png",
                    "subfolder": "",
                    "type": "output",
                }
            ],
        }


def approved_envelope(*, operation: str):
    return approved_execution_envelope(
        request_id=REQUEST_ID,
        operation=operation,
        target=COMFYUI_TARGET,
        approved_at=NOW,
    )


def unapproved_envelope():
    return unapproved_execution_envelope(
        request_id=REQUEST_ID,
        operation="image_generate",
        target=COMFYUI_TARGET,
    )


def test_image_generation_succeeds_with_mocked_approved_execution_envelope() -> None:
    client = MockComfyUIClient()
    adapter = ComfyUIAdapter(client)
    envelope = approved_envelope(operation="image_generate")
    workflow = {
        "prompt": "paint a quiet studio scene",
        "nodes": [{"id": "positive_prompt", "type": "CLIPTextEncode"}],
    }

    result = adapter.generate_image(
        ComfyUIImageGenerationRequest(
            prompt="paint a quiet studio scene",
            workflow=workflow,
            execution_envelope=envelope,
        ),
        now=NOW,
    )

    assert client.calls == [workflow]
    assert result.execution_envelope_id == envelope.execution_envelope_id
    assert result.request_id == REQUEST_ID
    assert result.operation == "image_generate"
    assert result.client_response["prompt_id"] == "mock-prompt-001"


@pytest.mark.parametrize(
    ("envelope", "expected_reason"),
    [
        (None, "requires an execution envelope"),
        ({"operation": "image_generate"}, "invalid"),
        (unapproved_envelope(), "not valid"),
        (
            approved_envelope(operation="image_generate").model_copy(update={"allow": False}),
            "does not allow execution",
        ),
        (approved_envelope(operation="publish"), "operation must be image_generate"),
        (
            approved_envelope(operation="image_generate").model_copy(
                update={"expires_at": NOW - timedelta(seconds=1)}
            ),
            "expired",
        ),
        (
            approved_envelope(operation="image_generate").model_copy(update={"signature": ""}),
            "signature",
        ),
    ],
)
def test_image_generation_fails_without_valid_execution_envelope(
    envelope: object,
    expected_reason: str,
) -> None:
    client = MockComfyUIClient()
    adapter = ComfyUIAdapter(client)

    with pytest.raises(ComfyUIExecutionGateError, match=expected_reason):
        adapter.generate_image(
            ComfyUIImageGenerationRequest(
                prompt="paint a quiet studio scene",
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
    imported_names = {
        (node.module, alias.name)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }

    assert "approved_execution_envelope(" in contents
    assert "unapproved_execution_envelope(" in contents
    assert ("backend.schemas", "ExecutionEnvelopeRequest") not in imported_names
    assert ("backend.service", "create_execution_envelope") not in imported_names
