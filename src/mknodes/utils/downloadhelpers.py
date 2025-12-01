from __future__ import annotations

import os
from urllib import parse

import anyenv

from mknodes.utils import log


logger = log.get_logger(__name__)


def _get_headers(user_headers: dict[str, str] | None = None) -> dict[str, str]:
    """Build request headers including Github token if available."""
    headers: dict[str, str] = {}
    if token := os.getenv("GH_TOKEN"):
        headers["Authorization"] = f"token {token}"
    if user_headers:
        headers.update(user_headers)
    return headers


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
    content = anyenv.get_bytes_sync(url, cache=True, headers=_get_headers(headers))
    logger.debug("Downloaded %s", url)
    return content


async def download_async(url: str, headers: dict[str, str] | None = None) -> bytes:
    """Download a file from given URL asynchronously and return its content.

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

    response = await anyenv.get_bytes(url, headers=_get_headers(headers), cache=True)
    logger.debug("Downloaded %s", url)
    return response
