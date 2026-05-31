from pathlib import Path
from uuid import UUID

from backend.repo_paths import (
    backend_module_filenames,
    read_backend_module_text,
    repo_root_from,
)
from backend.runtime_ids import prefixed_runtime_id, runtime_uuid


REPO_ROOT = repo_root_from(Path(__file__))


def test_runtime_uuid_returns_valid_uuid() -> None:
    assert isinstance(runtime_uuid(), UUID)


def test_prefixed_runtime_id_uses_shared_runtime_uuid() -> None:
    runtime_id = prefixed_runtime_id("tool-call")
    prefix, raw_uuid = runtime_id.split(":", maxsplit=1)

    assert prefix == "tool-call"
    assert UUID(raw_uuid)


def test_backend_runtime_uuid_generation_uses_shared_helper() -> None:
    offenders: list[str] = []
    for module_filename in backend_module_filenames(REPO_ROOT):
        if module_filename == "runtime_ids.py":
            continue
        source = read_backend_module_text(module_filename, REPO_ROOT)
        if "uuid4" in source:
            offenders.append(module_filename)

    assert offenders == []
