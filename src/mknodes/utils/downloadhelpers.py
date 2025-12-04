from __future__ import annotations

from urllib import parse

import anyenv

from mknodes.utils import log


logger = log.get_logger(__name__)


def download(url: str, headers: dict[str, str] | None = None) -> bytes:
    """Download a file from given URL and return its content.

    If the URL is a local path, it is simply read and returned instead.

    Args:
        url: URL or local path of the file to use
        headers: Headers to use for the request

    Returns:
        The downloaded content as bytes
    """
    from upath import UPath

    logger.debug("Getting file for '%s'", url)
    if parse.urlsplit(url).scheme not in {"http", "https"}:
        path = UPath(url)
        return path.read_bytes()
    content = anyenv.get_bytes_sync(url, cache=True, headers=headers)
    logger.debug("Downloaded %s", url)
    return content
