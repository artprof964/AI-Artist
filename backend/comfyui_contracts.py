from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.payload_fields import optional_string_field, required_string_field
from backend.response_fields import field_value


COMFYUI_URI_SCHEME = "comfyui"
COMFYUI_DEFAULT_IMAGE_TYPE = "output"


def comfyui_image_storage_uri(
    image: Mapping[str, Any],
    *,
    error_type: type[Exception] = ValueError,
    filename_message: str = "generated image must include filename or storage_uri",
    type_message: str = "generated image type must be a non-empty string",
    subfolder_message: str = "generated image subfolder must be a string",
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
    "COMFYUI_URI_SCHEME",
    "comfyui_image_storage_uri",
]
