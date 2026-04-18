from datetime import date, datetime, timedelta, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def days_ago(days: int) -> datetime:
    return utc_now() - timedelta(days=days)


def ensure_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return datetime.fromisoformat(value).date()


def range_to_days(range_value: str) -> int:
    mapping = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365}
    return mapping.get(range_value.upper(), 90)
