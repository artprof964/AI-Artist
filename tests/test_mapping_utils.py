from backend.mapping_utils import copy_mapping, merge_mappings
from backend.repo_paths import backend_module_filenames, backend_module_path
from path_helpers import PROJECT_ROOT, read_backend_source


def test_copy_mapping_returns_mutable_copy_without_aliasing() -> None:
    original = {"sample": "ready"}
    copied = copy_mapping(original)

    copied["sample"] = "changed"

    assert original == {"sample": "ready"}
    assert copied == {"sample": "changed"}


def test_copy_mapping_treats_none_as_empty_mapping() -> None:
    assert copy_mapping(None) == {}


def test_merge_mappings_applies_later_values_last() -> None:
    assert merge_mappings({"title": "Original", "kind": "source"}, {"title": "Override"}) == {
        "title": "Override",
        "kind": "source",
    }


def test_backend_metadata_copies_use_shared_mapping_helper() -> None:
    forbidden_patterns = (
        "dict(metadata or {})",
        "dict(entry.metadata or {})",
        "dict(candidate.metadata)",
        "dict(document.metadata)",
        "dict(payload.get(\"metadata\") or {})",
        "dict(image)",
    )
    offenders: list[str] = []
    for module_filename in backend_module_filenames(PROJECT_ROOT):
        source = read_backend_source(module_filename)
        if any(pattern in source for pattern in forbidden_patterns):
            offenders.append(str(backend_module_path(module_filename)))

    assert offenders == []
