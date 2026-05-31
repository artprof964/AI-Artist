from pathlib import Path
import shutil

from backend.file_scanning import TEXT_REVIEW_SUFFIXES, iter_review_text_files
from backend.repo_paths import repo_root_from

REPO_ROOT = repo_root_from(Path(__file__))


def test_review_text_suffix_contract_covers_project_text_sources() -> None:
    assert TEXT_REVIEW_SUFFIXES == frozenset({".json", ".md", ".txt", ".yaml", ".yml"})


def test_iter_review_text_files_returns_sorted_supported_files() -> None:
    scratch_root = REPO_ROOT / ".codex_tmp" / "test_file_scanning"
    try:
        scratch_root.mkdir(parents=True, exist_ok=True)
        (scratch_root / "b.md").write_text("b", encoding="utf-8")
        (scratch_root / "a.txt").write_text("a", encoding="utf-8")
        (scratch_root / "skip.bin").write_bytes(b"nope")
        nested = scratch_root / "nested"
        nested.mkdir(exist_ok=True)
        (nested / "c.YAML").write_text("c", encoding="utf-8")

        assert [
            path.relative_to(scratch_root).as_posix()
            for path in iter_review_text_files(scratch_root)
        ] == [
            "a.txt",
            "b.md",
            "nested/c.YAML",
        ]
    finally:
        shutil.rmtree(scratch_root, ignore_errors=True)
