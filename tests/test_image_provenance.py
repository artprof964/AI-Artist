from datetime import datetime, timezone
import hashlib
import json

import pytest
from pydantic import ValidationError

from backend.image_provenance import (
    ImageProvenanceError,
    ImageProvenanceInput,
    LocalImageProvenanceStore,
    record_comfyui_image_provenance,
    record_generated_image_provenance,
    sha256_workflow,
)


NOW = datetime(2026, 5, 31, 9, 0, tzinfo=timezone.utc)
PROMPT = "paint a quiet studio scene"
WORKFLOW = {
    "nodes": [
        {"id": "positive_prompt", "type": "CLIPTextEncode", "inputs": {"text": PROMPT}},
        {"id": "sampler", "type": "KSampler", "inputs": {"seed": 424242}},
    ],
}
MODEL = "sdxl-local-art-v1"
SEED = 424242
SOURCE_REFS = [
    "source:trend-report:2026-05-31",
    "source:moodboard:studio-lighting",
]


def test_records_required_provenance_for_every_comfyui_image() -> None:
    store = LocalImageProvenanceStore()
    client_response = {
        "prompt_id": "mock-prompt-001",
        "images": [
            {
                "filename": "studio-0001.png",
                "subfolder": "approved",
                "type": "output",
            },
            {
                "filename": "studio-0002.png",
                "subfolder": "",
                "type": "output",
                "storage_uri": "local://artifacts/images/studio-0002.png",
            },
        ],
    }

    records = record_comfyui_image_provenance(
        prompt=PROMPT,
        workflow=WORKFLOW,
        model=MODEL,
        seed=SEED,
        source_refs=SOURCE_REFS,
        client_response=client_response,
        review_status="pending",
        store=store,
    )

    expected_prompt_hash = hashlib.sha256(PROMPT.encode("utf-8")).hexdigest()
    expected_workflow_hash = hashlib.sha256(
        json.dumps(
            WORKFLOW,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()

    assert len(records) == 2
    assert store.list_records() == records
    assert [record.storage_uri for record in records] == [
        "comfyui://output/approved/studio-0001.png",
        "local://artifacts/images/studio-0002.png",
    ]
    for record in records:
        assert record.prompt_hash == expected_prompt_hash
        assert record.workflow_hash == expected_workflow_hash
        assert record.model == MODEL
        assert record.seed == SEED
        assert record.source_refs == SOURCE_REFS
        assert record.review_status == "pending"
        assert store.get(record.image_id) == record


def test_workflow_hash_is_deterministic_for_equivalent_dict_order() -> None:
    first = {"b": 2, "a": {"z": [3, 2, 1], "m": "value"}}
    second = {"a": {"m": "value", "z": [3, 2, 1]}, "b": 2}

    assert sha256_workflow(first) == sha256_workflow(second)


@pytest.mark.parametrize("review_status", ["pending", "approved", "rejected"])
def test_all_allowed_review_status_values_are_accepted(review_status: str) -> None:
    store = LocalImageProvenanceStore()

    record = record_generated_image_provenance(
        {
            "prompt": PROMPT,
            "workflow": WORKFLOW,
            "model": MODEL,
            "seed": SEED,
            "source_refs": SOURCE_REFS,
            "storage_uri": f"local://artifacts/images/{review_status}.png",
            "review_status": review_status,
            "created_at": NOW,
        },
        store=store,
    )

    assert record.review_status == review_status


@pytest.mark.parametrize(
    "missing_field",
    [
        "prompt",
        "workflow",
        "model",
        "seed",
        "source_refs",
        "storage_uri",
        "review_status",
    ],
)
def test_rejects_missing_required_provenance_fields(missing_field: str) -> None:
    payload = {
        "prompt": PROMPT,
        "workflow": WORKFLOW,
        "model": MODEL,
        "seed": SEED,
        "source_refs": SOURCE_REFS,
        "storage_uri": "local://artifacts/images/studio.png",
        "review_status": "pending",
    }
    payload.pop(missing_field)

    with pytest.raises(ValidationError):
        ImageProvenanceInput.model_validate(payload)


def test_rejects_empty_source_refs() -> None:
    with pytest.raises(ValidationError):
        ImageProvenanceInput.model_validate(
            {
                "prompt": PROMPT,
                "workflow": WORKFLOW,
                "model": MODEL,
                "seed": SEED,
                "source_refs": [],
                "storage_uri": "local://artifacts/images/studio.png",
                "review_status": "pending",
            }
        )


def test_rejects_invalid_review_status() -> None:
    with pytest.raises(ValidationError):
        ImageProvenanceInput.model_validate(
            {
                "prompt": PROMPT,
                "workflow": WORKFLOW,
                "model": MODEL,
                "seed": SEED,
                "source_refs": SOURCE_REFS,
                "storage_uri": "local://artifacts/images/studio.png",
                "review_status": "needs_review",
            }
        )


def test_rejects_comfyui_image_without_storage_reference() -> None:
    with pytest.raises(ImageProvenanceError, match="filename or storage_uri"):
        record_comfyui_image_provenance(
            prompt=PROMPT,
            workflow=WORKFLOW,
            model=MODEL,
            seed=SEED,
            source_refs=SOURCE_REFS,
            client_response={"images": [{"subfolder": "", "type": "output"}]},
            review_status="pending",
            store=LocalImageProvenanceStore(),
        )
