from datetime import UTC, datetime, timedelta, timezone

from backend.time_utils import as_utc, utc_now


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
