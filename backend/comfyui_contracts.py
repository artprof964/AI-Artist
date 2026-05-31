from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.payload_fields import optional_string_field, required_string_field
from backend.response_fields import field_value


COMFYUI_URI_SCHEME = "comfyui"
COMFYUI_DEFAULT_IMAGE_TYPE = "output"
COMFYUI_IMAGE_FILENAME_MESSAGE = "generated image must include filename or storage_uri"
COMFYUI_IMAGE_TYPE_MESSAGE = "generated image type must be a non-empty string"
COMFYUI_IMAGE_SUBFOLDER_MESSAGE = "generated image subfolder must be a string"
COMFYUI_RESPONSE_IMAGES_REQUIRED = "client response must include generated images"
COMFYUI_RESPONSE_IMAGE_ENTRY_REQUIRED = "generated image entries must be objects"


def comfyui_image_storage_uri(
    image: Mapping[str, Any],
    *,
    error_type: type[Exception] = ValueError,
    filename_message: str = COMFYUI_IMAGE_FILENAME_MESSAGE,
    type_message: str = COMFYUI_IMAGE_TYPE_MESSAGE,
    subfolder_message: str = COMFYUI_IMAGE_SUBFOLDER_MESSAGE,
) -> str:
    filename = required_string_field(
        image,
        "filename",
        error_type=error_type,
        message=filename_message,
    )
    image_type = required_string_field(
        {"type": field_value(image, "type", COMFYUI_DEFAULT_IMAGE_TYPE)},
        "type",
        error_type=error_type,
        message=type_message,
    )
    subfolder = (
        optional_string_field(
            image,
            "subfolder",
            error_type=error_type,
            message=subfolder_message,
        )
        or ""
    )

    normalized_subfolder = subfolder.strip("/")
    if normalized_subfolder:
        return f"{COMFYUI_URI_SCHEME}://{image_type}/{normalized_subfolder}/{filename}"
    return f"{COMFYUI_URI_SCHEME}://{image_type}/{filename}"


__all__ = [
    "COMFYUI_DEFAULT_IMAGE_TYPE",
    "COMFYUI_IMAGE_FILENAME_MESSAGE",
    "COMFYUI_IMAGE_SUBFOLDER_MESSAGE",
    "COMFYUI_IMAGE_TYPE_MESSAGE",
    "COMFYUI_RESPONSE_IMAGE_ENTRY_REQUIRED",
    "COMFYUI_RESPONSE_IMAGES_REQUIRED",
    "COMFYUI_URI_SCHEME",
    "comfyui_image_storage_uri",
]
