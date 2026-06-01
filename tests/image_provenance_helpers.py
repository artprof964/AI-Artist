from datetime import datetime, timezone
from typing import Any

from backend.image_provenance import ImageProvenanceRecord, LocalImageProvenanceStore

PROVENANCE_TEST_CREATED_AT = datetime(2026, 5, 31, 9, 0, tzinfo=timezone.utc)
PROVENANCE_TEST_PROMPT = "paint a quiet studio scene"
PROVENANCE_TEST_WORKFLOW = {
    "nodes": [
        {
            "id": "positive_prompt",
            "type": "CLIPTextEncode",
            "inputs": {"text": PROVENANCE_TEST_PROMPT},
        },
        {"id": "sampler", "type": "KSampler", "inputs": {"seed": 424242}},
    ],
}
PROVENANCE_TEST_MODEL = "sdxl-local-art-v1"
PROVENANCE_TEST_SEED = 424242
PROVENANCE_TEST_SOURCE_REFS = [
    "source:trend-report:2026-05-31",
    "source:moodboard:studio-lighting",
]
PROVENANCE_TEST_STORAGE_URI = "local://artifacts/images/studio-hero-001.png"
PROVENANCE_TEST_REVIEW_STATUS = "pending"


def image_provenance_store_for_test() -> LocalImageProvenanceStore:
    return LocalImageProvenanceStore()


def image_provenance_payload_for_test(
    *,
    prompt: str = PROVENANCE_TEST_PROMPT,
    workflow: dict[str, Any] | None = None,
    model: str = PROVENANCE_TEST_MODEL,
    seed: int = PROVENANCE_TEST_SEED,
    source_refs: list[str] | None = None,
    storage_uri: str = PROVENANCE_TEST_STORAGE_URI,
    review_status: str = PROVENANCE_TEST_REVIEW_STATUS,
    created_at: datetime = PROVENANCE_TEST_CREATED_AT,
    image_id: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "prompt": prompt,
        "workflow": workflow or dict(PROVENANCE_TEST_WORKFLOW),
        "model": model,
        "seed": seed,
        "source_refs": list(source_refs or PROVENANCE_TEST_SOURCE_REFS),
        "storage_uri": storage_uri,
        "review_status": review_status,
        "created_at": created_at,
    }
    if image_id is not None:
        payload["image_id"] = image_id
    return payload


def image_provenance_record_for_test(
    *,
    image_id: str = "studio-hero-001",
    prompt_hash: str = "prompt-hash",
    workflow_hash: str = "workflow-hash",
    model: str = PROVENANCE_TEST_MODEL,
    seed: int = PROVENANCE_TEST_SEED,
    source_refs: list[str] | None = None,
    storage_uri: str = PROVENANCE_TEST_STORAGE_URI,
    review_status: str = PROVENANCE_TEST_REVIEW_STATUS,
    created_at: datetime = PROVENANCE_TEST_CREATED_AT,
) -> ImageProvenanceRecord:
    return ImageProvenanceRecord(
        image_id=image_id,
        prompt_hash=prompt_hash,
        workflow_hash=workflow_hash,
        model=model,
        seed=seed,
        source_refs=list(source_refs or PROVENANCE_TEST_SOURCE_REFS),
        storage_uri=storage_uri,
        review_status=review_status,
        created_at=created_at,
    )
