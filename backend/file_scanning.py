from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path


TEXT_REVIEW_SUFFIXES = frozenset({".json", ".md", ".txt", ".yaml", ".yml"})


def iter_review_text_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return ()
    return (
        path
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.suffix.lower() in TEXT_REVIEW_SUFFIXES
    )


__all__ = [
    "TEXT_REVIEW_SUFFIXES",
    "iter_review_text_files",
]
