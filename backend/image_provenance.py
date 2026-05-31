from __future__ import annotations

from datetime import datetime, timezone
from threading import RLock
from typing import Any, Literal, Protocol

from backend.canonical_hash import sha256_json, sha256_text as canonical_sha256_text
from backend.model_coercion import coerce_model
from backend.payload_fields import optional_string_field, required_string_field
from backend.time_utils import as_utc
from pydantic import BaseModel, ConfigDict, Field


ReviewStatus = Literal["pending", "approved", "rejected"]


class ImageProvenanceError(ValueError):
    """Raised when image provenance cannot be recorded safely."""


class ImageProvenanceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(min_length=1)
    workflow: dict[str, Any] = Field(min_length=1)
    model: str = Field(min_length=1)
    seed: int
    source_refs: list[str] = Field(min_length=1)
    storage_uri: str = Field(min_length=1)
    review_status: ReviewStatus
    image_id: str | None = Field(default=None, min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ImageProvenanceRecord(BaseModel):
    image_id: str
    prompt_hash: str
    workflow_hash: str
    model: str
    seed: int
    source_refs: list[str]
    storage_uri: str
    review_status: ReviewStatus
    created_at: datetime


class ImageProvenanceStore(Protocol):
    def record(self, provenance: ImageProvenanceInput | dict[str, Any]) -> ImageProvenanceRecord:
        ...

    def list_records(self) -> list[ImageProvenanceRecord]:
        ...

    def get(self, image_id: str) -> ImageProvenanceRecord | None:
        ...

    def clear(self) -> None:
        ...


class LocalImageProvenanceStore:
    """Deterministic in-process provenance store for generated image artifacts."""

    def __init__(self) -> None:
        self._records: dict[str, ImageProvenanceRecord] = {}
        self._order: list[str] = []
        self._lock = RLock()

    def record(self, provenance: ImageProvenanceInput | dict[str, Any]) -> ImageProvenanceRecord:
        payload = _coerce_provenance_input(provenance)
        prompt_hash = sha256_text(payload.prompt)
        workflow_hash = sha256_workflow(payload.workflow)
        image_id = payload.image_id or deterministic_image_id(
            prompt_hash=prompt_hash,
            workflow_hash=workflow_hash,
            model=payload.model,
            seed=payload.seed,
            storage_uri=payload.storage_uri,
        )
        record = ImageProvenanceRecord(
            image_id=image_id,
            prompt_hash=prompt_hash,
            workflow_hash=workflow_hash,
            model=payload.model,
            seed=payload.seed,
            source_refs=list(payload.source_refs),
            storage_uri=payload.storage_uri,
            review_status=payload.review_status,
            created_at=_as_utc(payload.created_at),
        )

        with self._lock:
            if image_id not in self._records:
                self._order.append(image_id)
            self._records[image_id] = record
        return record

    def list_records(self) -> list[ImageProvenanceRecord]:
        with self._lock:
            return [self._records[image_id] for image_id in self._order]

    def get(self, image_id: str) -> ImageProvenanceRecord | None:
        with self._lock:
            return self._records.get(image_id)

    def clear(self) -> None:
        with self._lock:
            self._records.clear()
            self._order.clear()


image_provenance_store = LocalImageProvenanceStore()


def record_generated_image_provenance(
    provenance: ImageProvenanceInput | dict[str, Any],
    *,
    store: ImageProvenanceStore = image_provenance_store,
) -> ImageProvenanceRecord:
    return store.record(provenance)


def record_comfyui_image_provenance(
    *,
    prompt: str,
    workflow: dict[str, Any],
    model: str,
    seed: int,
    source_refs: list[str],
    client_response: dict[str, Any],
    review_status: ReviewStatus,
    store: ImageProvenanceStore = image_provenance_store,
) -> list[ImageProvenanceRecord]:
    images = client_response.get("images")
    if not isinstance(images, list) or not images:
        raise ImageProvenanceError("client response must include generated images")

    records: list[ImageProvenanceRecord] = []
    for image in images:
        if not isinstance(image, dict):
            raise ImageProvenanceError("generated image entries must be objects")

        records.append(
            store.record(
                {
                    "prompt": prompt,
                    "workflow": workflow,
                    "model": model,
                    "seed": seed,
                    "source_refs": source_refs,
                    "storage_uri": image.get("storage_uri") or _storage_uri_from_comfyui_image(image),
                    "review_status": review_status,
                }
            )
        )
    return records


def sha256_text(value: str) -> str:
    return canonical_sha256_text(value)


def sha256_workflow(workflow: dict[str, Any]) -> str:
    return sha256_json(workflow, ensure_ascii=False)


def deterministic_image_id(
    *,
    prompt_hash: str,
    workflow_hash: str,
    model: str,
    seed: int,
    storage_uri: str,
) -> str:
    material = {
        "model": model,
        "prompt_hash": prompt_hash,
        "seed": seed,
        "storage_uri": storage_uri,
        "workflow_hash": workflow_hash,
    }
    return sha256_json(material, ensure_ascii=False)


def _coerce_provenance_input(
    provenance: ImageProvenanceInput | dict[str, Any],
) -> ImageProvenanceInput:
    return coerce_model(provenance, ImageProvenanceInput)


def _storage_uri_from_comfyui_image(image: dict[str, Any]) -> str:
    filename = required_string_field(
        image,
        "filename",
        error_type=ImageProvenanceError,
        message="generated image must include filename or storage_uri",
    )
    image_type = required_string_field(
        {"type": image.get("type", "output")},
        "type",
        error_type=ImageProvenanceError,
        message="generated image type must be a non-empty string",
    )
    subfolder = (
        optional_string_field(
            image,
            "subfolder",
            error_type=ImageProvenanceError,
            message="generated image subfolder must be a string",
        )
        or ""
    )

    normalized_subfolder = subfolder.strip("/")
    if normalized_subfolder:
        return f"comfyui://{image_type}/{normalized_subfolder}/{filename}"
    return f"comfyui://{image_type}/{filename}"


def _as_utc(value: datetime) -> datetime:
    return as_utc(value)


__all__ = [
    "ImageProvenanceError",
    "ImageProvenanceInput",
    "ImageProvenanceRecord",
    "ImageProvenanceStore",
    "LocalImageProvenanceStore",
    "ReviewStatus",
    "deterministic_image_id",
    "image_provenance_store",
    "record_comfyui_image_provenance",
    "record_generated_image_provenance",
    "sha256_text",
    "sha256_workflow",
]
