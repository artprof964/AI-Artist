from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

from backend.time_utils import as_utc, utc_now


PROJECT_ROOT = Path(__file__).resolve().parents[1]


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
    for source_path in (PROJECT_ROOT / "backend").glob("*.py"):
        text = source_path.read_text(encoding="utf-8")
        if "def _as_utc(" in text or "def _as_aware_utc(" in text:
            offenders.append(source_path.name)

    assert offenders == []
