import pytest

from backend.comfyui_contracts import (
    COMFYUI_DEFAULT_IMAGE_TYPE,
    COMFYUI_URI_SCHEME,
    comfyui_image_storage_uri,
)


class CustomComfyUIError(ValueError):
    pass


def test_comfyui_image_storage_uri_uses_shared_uri_convention() -> None:
    assert COMFYUI_URI_SCHEME == "comfyui"
    assert COMFYUI_DEFAULT_IMAGE_TYPE == "output"
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
