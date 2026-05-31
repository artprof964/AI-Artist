from collections.abc import Iterable, Iterator
from pathlib import Path

from backend.repo_paths import read_backend_module_text, read_repo_text, repo_root_from

PROJECT_ROOT = repo_root_from(Path(__file__))
TESTS_DIR = Path("tests")


def read_backend_source(module_filename: str) -> str:
    return read_backend_module_text(module_filename, PROJECT_ROOT)


def read_test_source(test_filename: str) -> str:
    return read_repo_text(PROJECT_ROOT, TESTS_DIR / test_filename)


def iter_test_module_sources(
    *, exclude: Iterable[str] = ()
) -> Iterator[tuple[str, str]]:
    excluded = set(exclude)
    for test_path in sorted((PROJECT_ROOT / TESTS_DIR).glob("test_*.py")):
        if test_path.name not in excluded:
            yield test_path.name, read_test_source(test_path.name)
