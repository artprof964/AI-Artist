from pathlib import Path

from backend.mapping_utils import copy_mapping, merge_mappings


REPO_ROOT = Path(__file__).resolve().parents[1]


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
    for path in (REPO_ROOT / "backend").glob("*.py"):
        source = path.read_text(encoding="utf-8")
        if any(pattern in source for pattern in forbidden_patterns):
            offenders.append(str(path.relative_to(REPO_ROOT)))

    assert offenders == []
