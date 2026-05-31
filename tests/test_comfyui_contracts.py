import pytest

from backend.comfyui_contracts import (
    COMFYUI_DEFAULT_IMAGE_TYPE,
    COMFYUI_IMAGE_FILENAME_MESSAGE,
    COMFYUI_IMAGE_SUBFOLDER_MESSAGE,
    COMFYUI_IMAGE_TYPE_MESSAGE,
    COMFYUI_RESPONSE_IMAGE_ENTRY_REQUIRED,
    COMFYUI_RESPONSE_IMAGES_REQUIRED,
    COMFYUI_URI_SCHEME,
    comfyui_image_storage_uri,
)


class CustomComfyUIError(ValueError):
    pass


def test_comfyui_image_storage_uri_uses_shared_uri_convention() -> None:
    assert COMFYUI_URI_SCHEME == "comfyui"
    assert COMFYUI_DEFAULT_IMAGE_TYPE == "output"
    assert COMFYUI_IMAGE_FILENAME_MESSAGE == "generated image must include filename or storage_uri"
    assert COMFYUI_IMAGE_TYPE_MESSAGE == "generated image type must be a non-empty string"
    assert COMFYUI_IMAGE_SUBFOLDER_MESSAGE == "generated image subfolder must be a string"
    assert COMFYUI_RESPONSE_IMAGES_REQUIRED == "client response must include generated images"
    assert COMFYUI_RESPONSE_IMAGE_ENTRY_REQUIRED == "generated image entries must be objects"
    assert (
        comfyui_image_storage_uri(
            {
                "filename": "studio.png",
                "subfolder": "/approved/",
                "type": "output",
            }
        )
        == "comfyui://output/approved/studio.png"
    )


def test_comfyui_image_storage_uri_defaults_to_output_without_subfolder() -> None:
    assert comfyui_image_storage_uri({"filename": "studio.png"}) == (
        "comfyui://output/studio.png"
    )


def test_comfyui_image_storage_uri_allows_custom_error_type() -> None:
    with pytest.raises(CustomComfyUIError, match="missing file"):
        comfyui_image_storage_uri(
            {"subfolder": "approved"},
            error_type=CustomComfyUIError,
            filename_message="missing file",
        )
