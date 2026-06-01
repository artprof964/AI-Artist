import ast

import pytest
from pydantic import ValidationError

from backend.canonical_hash import sha256_json, sha256_text
from backend.image_provenance import (
    ImageProvenanceError,
    ImageProvenanceInput,
    record_comfyui_image_provenance,
    record_generated_image_provenance,
    sha256_workflow,
)
from image_provenance_helpers import (
    PROVENANCE_TEST_MODEL,
    PROVENANCE_TEST_PROMPT,
    PROVENANCE_TEST_SEED,
    PROVENANCE_TEST_SOURCE_REFS,
    PROVENANCE_TEST_WORKFLOW,
    image_provenance_payload_for_test,
    image_provenance_store_for_test,
)
from path_helpers import read_backend_source, read_test_source


def test_records_required_provenance_for_every_comfyui_image() -> None:
    store = image_provenance_store_for_test()
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
        prompt=PROVENANCE_TEST_PROMPT,
        workflow=PROVENANCE_TEST_WORKFLOW,
        model=PROVENANCE_TEST_MODEL,
        seed=PROVENANCE_TEST_SEED,
        source_refs=PROVENANCE_TEST_SOURCE_REFS,
        client_response=client_response,
        review_status="pending",
        store=store,
    )

    expected_prompt_hash = sha256_text(PROVENANCE_TEST_PROMPT)
    expected_workflow_hash = sha256_json(PROVENANCE_TEST_WORKFLOW, ensure_ascii=False)

    assert len(records) == 2
    assert store.list_records() == records
    assert [record.storage_uri for record in records] == [
        "comfyui://output/approved/studio-0001.png",
        "local://artifacts/images/studio-0002.png",
    ]
    for record in records:
        assert record.prompt_hash == expected_prompt_hash
        assert record.workflow_hash == expected_workflow_hash
        assert record.model == PROVENANCE_TEST_MODEL
        assert record.seed == PROVENANCE_TEST_SEED
        assert record.source_refs == PROVENANCE_TEST_SOURCE_REFS
        assert record.review_status == "pending"
        assert store.get(record.image_id) == record


def test_workflow_hash_is_deterministic_for_equivalent_dict_order() -> None:
    first = {"b": 2, "a": {"z": [3, 2, 1], "m": "value"}}
    second = {"a": {"m": "value", "z": [3, 2, 1]}, "b": 2}

    assert sha256_workflow(first) == sha256_workflow(second)


@pytest.mark.parametrize("review_status", ["pending", "approved", "rejected"])
def test_all_allowed_review_status_values_are_accepted(review_status: str) -> None:
    store = image_provenance_store_for_test()

    record = record_generated_image_provenance(
        image_provenance_payload_for_test(
            storage_uri=f"local://artifacts/images/{review_status}.png",
            review_status=review_status,
        ),
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
        "prompt": PROVENANCE_TEST_PROMPT,
        "workflow": PROVENANCE_TEST_WORKFLOW,
        "model": PROVENANCE_TEST_MODEL,
        "seed": PROVENANCE_TEST_SEED,
        "source_refs": PROVENANCE_TEST_SOURCE_REFS,
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
                "prompt": PROVENANCE_TEST_PROMPT,
                "workflow": PROVENANCE_TEST_WORKFLOW,
                "model": PROVENANCE_TEST_MODEL,
                "seed": PROVENANCE_TEST_SEED,
                "source_refs": [],
                "storage_uri": "local://artifacts/images/studio.png",
                "review_status": "pending",
            }
        )


def test_rejects_invalid_review_status() -> None:
    with pytest.raises(ValidationError):
        ImageProvenanceInput.model_validate(
            {
                "prompt": PROVENANCE_TEST_PROMPT,
                "workflow": PROVENANCE_TEST_WORKFLOW,
                "model": PROVENANCE_TEST_MODEL,
                "seed": PROVENANCE_TEST_SEED,
                "source_refs": PROVENANCE_TEST_SOURCE_REFS,
                "storage_uri": "local://artifacts/images/studio.png",
                "review_status": "needs_review",
            }
        )


def test_rejects_comfyui_image_without_storage_reference() -> None:
    with pytest.raises(ImageProvenanceError, match="filename or storage_uri"):
        record_comfyui_image_provenance(
            prompt=PROVENANCE_TEST_PROMPT,
            workflow=PROVENANCE_TEST_WORKFLOW,
            model=PROVENANCE_TEST_MODEL,
            seed=PROVENANCE_TEST_SEED,
            source_refs=PROVENANCE_TEST_SOURCE_REFS,
            client_response={"images": [{"subfolder": "", "type": "output"}]},
            review_status="pending",
            store=image_provenance_store_for_test(),
        )


def test_image_provenance_uses_shared_comfyui_storage_uri_contract() -> None:
    source = read_backend_source("image_provenance.py")

    assert "def _storage_uri_from_comfyui_image(" not in source
    assert "comfyui_image_storage_reference(" in source
    assert "comfyui_image_storage_uri(" not in source
    assert '"client response must include generated images"' not in source
    assert '"generated image entries must be objects"' not in source
    assert 'client_response,\n        "images"' not in source
    assert 'field_value(image_response, "storage_uri")' not in source
    assert "COMFYUI_RESPONSE_IMAGES_REQUIRED" in source
    assert "COMFYUI_RESPONSE_IMAGE_ENTRY_REQUIRED" in source
    assert "COMFYUI_RESPONSE_IMAGES_FIELD" in source


def test_image_provenance_uses_shared_model_coercion_directly() -> None:
    source = read_backend_source("image_provenance.py")

    assert "def _coerce_provenance_input(" not in source
    assert "coerce_model(provenance, ImageProvenanceInput)" in source


def test_image_provenance_uses_canonical_text_hash_directly() -> None:
    source = read_backend_source("image_provenance.py")

    assert "def sha256_text(" not in source
    assert "from backend.canonical_hash import sha256_json, sha256_text" in source
    assert "prompt_hash = sha256_text(payload.prompt)" in source


def test_image_provenance_tests_use_shared_provenance_helpers() -> None:
    for test_module in (
        "test_image_provenance.py",
        "test_critic_curator.py",
        "test_security_review.py",
    ):
        source = read_test_source(test_module)
        tree = ast.parse(source)
        imported_names = {
            (node.module, alias.name)
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }
        called_names = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }

        assert called_names & {
            "image_provenance_store_for_test",
            "image_provenance_payload_for_test",
            "image_provenance_record_for_test",
        }
        assert ("backend.image_provenance", "LocalImageProvenanceStore") not in imported_names
        assert ("backend.image_provenance", "ImageProvenanceRecord") not in imported_names
