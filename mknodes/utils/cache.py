from __future__ import annotations

from contextlib import contextmanager
import datetime
import hashlib
import logging
import os
import pathlib
import tempfile as tmp

from urllib import parse, request

import platformdirs


logger = logging.getLogger(__name__)


@contextmanager
def tempfile(suffix="", directory=None):
    """Context for temporary file.

    Will find a free temporary filename upon entering
    and will try to delete the file on leaving, even in case of an exception.

    Arguments:
        suffix : optional file suffix
        directory : optional directory to save temporary file in
    """
    tf = tmp.NamedTemporaryFile(delete=False, suffix=suffix, dir=directory)
    tf.file.close()
    try:
        yield tf.name
    finally:
        try:
            pathlib.Path(tf.name).unlink()
        except OSError as e:
            if e.errno != 2:  # noqa: PLR2004
                raise


@contextmanager
def open_atomic(filepath, fsync: bool = False, binary: bool = False):
    """Open temporary file object that atomically moves to destination upon exiting.

    Allows reading and writing to and from the same filename.

    The file will not be moved to destination in case of an exception.

    Arguments:
        filepath : the file path to be opened
        fsync : whether to force write the file to disk
        binary: Whether to open in binary mode
    """
    abs_path = pathlib.Path(filepath).resolve()
    with tempfile(directory=abs_path.parent) as tmppath:
        path = pathlib.Path(tmppath)
        with path.open(mode="wb" if binary else "w") as file:
            try:
                yield file
            finally:
                if fsync:
                    file.flush()
                    os.fsync(file.fileno())
        if abs_path.exists():
            abs_path.unlink()
        os.rename(path, abs_path)  # noqa: PTH104


def download_and_cache_url(
    url: str,
    days: int = 0,
    seconds: int = 0,
    microseconds: int = 0,
    milliseconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    weeks: int = 0,
    comment: bytes = b"# ",
) -> bytes:
    """Downloads a file from the URL, stores it under ~/.cache/, and returns its content.

    If the URL is a local path, it is simply read and returned instead.

    For tracking the age of the content, a prefix is inserted into the stored file,
    rather than relying on mtime.

    Arguments:
        url: URL or local path of the file to use.
        days: Amount of days the content should be cached.
        seconds: Amount of seconds the content should be cached.
        microseconds: Amount of microseconds the content should be cached.
        milliseconds: Amount of milliseconds the content should be cached.
        minutes: Amount of minutes the content should be cached.
        hours: Amount of hours the content should be cached.
        weeks: Amount of weeks the content should be cached.
        comment: The appropriate comment prefix for this file format.
    """
    logger.info("Getting %s", url)
    if parse.urlsplit(url).scheme not in ("http", "https"):
        with pathlib.Path(url).open("rb") as f:
            return f.read()
    cache_duration = datetime.timedelta(
        days=days,
        seconds=seconds,
        microseconds=microseconds,
        milliseconds=milliseconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks,
    )
    path = platformdirs.user_cache_dir("mknodes")
    directory = pathlib.Path(path) / "mknodes_url_cache"
    name_hash = hashlib.sha256(url.encode()).hexdigest()[:32]
    path = directory / (name_hash + os.path.splitext(url)[1])  # noqa: PTH122

    now = int(datetime.datetime.now(datetime.UTC).timestamp())
    prefix = b"%s%s downloaded at timestamp " % (comment, url.encode())
    # Check for cached file and try to return it
    path = pathlib.Path(path)
    if path.is_file():
        try:
            with path.open("rb") as f:
                line = f.readline()
                if line.startswith(prefix):
                    line = line[len(prefix) :]
                    timestamp = int(line)
                    if datetime.timedelta(seconds=(now - timestamp)) <= cache_duration:
                        logger.debug("Using cached '%s' for '%s'", path, url)
                        return f.read()
        except (OSError, ValueError) as e:
            logger.debug("%s: %s", type(e).__name__, e)

    # Download and cache the file
    logger.debug("Downloading %s to %s", url, path)
    content = download(url)
    directory.mkdir(exist_ok=True, parents=True)
    with open_atomic(str(path), binary=True) as f:
        f.write(b"%s%d\n" % (prefix, now))
        f.write(content)
    logger.info("Downloaded %s", url)
    return content


def download(url: str):
    req = request.Request(url)
    if token := os.getenv("GH_TOKEN"):
        req.add_header("Authorization", f"token {token}")
    with request.urlopen(req) as resp:
        return resp.read()


if __name__ == "__main__":
    a = download_and_cache_url("https://docs.python.org/3/objects.inv")
    print(a)
