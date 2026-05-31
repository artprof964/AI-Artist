from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import pytest

from backend.comfyui_adapter import (
    ComfyUIAdapter,
    ComfyUIExecutionGateError,
    ComfyUIImageGenerationRequest,
)
from backend.repo_paths import read_backend_module_text
from backend.schemas import ExecutionEnvelopeRequest, HumanApproval, SourceFreshness
from backend.service import create_execution_envelope


REQUEST_ID = UUID("17171717-1717-1717-1717-171717171717")
NOW = datetime.now(timezone.utc)


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
    return create_execution_envelope(
        ExecutionEnvelopeRequest(
            request_id=REQUEST_ID,
            request_kind="action",
            operation=operation,
            requester_scope="user:local",
            policy_scope="workspace:ai-artist-main",
            target="comfyui://workflow/mock-image-generation",
            human_approval=HumanApproval(
                approved=True,
                approver_scope="user:owner",
                approved_at=NOW,
            ),
            source_freshness=SourceFreshness(
                all_required_sources_unchanged=True,
                changed_source_count=0,
            ),
        )
    )


def unapproved_envelope():
    return create_execution_envelope(
        ExecutionEnvelopeRequest(
            request_id=REQUEST_ID,
            request_kind="action",
            operation="image_generate",
            requester_scope="user:local",
            policy_scope="workspace:ai-artist-main",
            target="comfyui://workflow/mock-image-generation",
            human_approval=HumanApproval(approved=False),
            source_freshness=SourceFreshness(
                all_required_sources_unchanged=True,
                changed_source_count=0,
            ),
        )
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
    contents = read_backend_module_text("comfyui_adapter.py")

    assert "IMAGE_GENERATE_OPERATION =" not in contents
    assert "operation=OPERATION_IMAGE_GENERATE" in contents


def test_comfyui_adapter_uses_shared_missing_envelope_message() -> None:
    contents = read_backend_module_text("comfyui_adapter.py")

    assert '"image generation requires an execution envelope"' not in contents
    assert 'execution_envelope_required("image generation")' in contents
