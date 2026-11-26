"""The build time: one timestamp per process, `SOURCE_DATE_EPOCH` for reproducible builds."""

import datetime as dt
import functools
import os


@functools.cache
def build_time() -> dt.datetime:
    """Return the time of the build (UTC, timezone-aware).

    Taken once per process, so every page / template sees the same time. If the
    `SOURCE_DATE_EPOCH` environment variable is set (reproducible builds, see
    https://reproducible-builds.org/specs/source-date-epoch/), that time is used.
    """
    if epoch := os.environ.get("SOURCE_DATE_EPOCH", "").strip():
        return dt.datetime.fromtimestamp(int(epoch), tz=dt.UTC)
    return dt.datetime.now(dt.UTC)


def now(tz: dt.tzinfo | None = None) -> dt.datetime:
    """`now()` for templates: the build time (naive local time, or in given time zone)."""
    if tz is None:
        return build_time().astimezone().replace(tzinfo=None)
    return build_time().astimezone(tz)


def utcnow() -> dt.datetime:
    """`utcnow()` for templates: the build time in UTC."""
    return build_time()
