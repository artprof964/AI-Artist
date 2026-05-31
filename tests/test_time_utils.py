from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

from backend.repo_paths import (
    backend_module_filenames,
    read_backend_module_text,
    read_repo_text,
    repo_root_from,
)
from backend.time_utils import as_utc, utc_now


PROJECT_ROOT = repo_root_from(Path(__file__))


def test_utc_now_returns_timezone_aware_utc_datetime() -> None:
    value = utc_now()

    assert value.tzinfo is not None
    assert value.utcoffset() == timedelta(0)


def test_as_utc_treats_naive_datetimes_as_utc() -> None:
    assert as_utc(datetime(2026, 5, 31, 12, 0)) == datetime(2026, 5, 31, 12, 0, tzinfo=UTC)


def test_as_utc_keeps_utc_datetimes_unchanged() -> None:
    value = datetime(2026, 5, 31, 12, 0, tzinfo=UTC)

    assert as_utc(value) == value


def test_as_utc_converts_aware_offsets_to_utc() -> None:
    vienna = timezone(timedelta(hours=2))

    assert as_utc(datetime(2026, 5, 31, 14, 0, tzinfo=vienna)) == datetime(
        2026, 5, 31, 12, 0, tzinfo=UTC
    )


def test_backend_modules_do_not_wrap_shared_utc_normalization() -> None:
    offenders = []
    for module_filename in backend_module_filenames(PROJECT_ROOT):
        text = read_backend_module_text(module_filename, PROJECT_ROOT)
        if "def _as_utc(" in text or "def _as_aware_utc(" in text:
            offenders.append(module_filename)

    assert offenders == []


def test_tests_use_shared_utc_now_helper_for_current_time() -> None:
    offenders: list[str] = []

    for test_path in sorted((PROJECT_ROOT / "tests").glob("test_*.py")):
        if test_path.name == "test_time_utils.py":
            continue
        source = read_repo_text(PROJECT_ROOT, Path("tests") / test_path.name)
        if "datetime.now(timezone.utc)" in source:
            offenders.append(test_path.name)

    assert offenders == []
