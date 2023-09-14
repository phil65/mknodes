from __future__ import annotations

import os
import pathlib

from urllib import parse

import requests
import requests_cache

from mknodes.utils import log


logger = log.get_logger(__name__)


requests_cache.install_cache(
    cache_control=True,
    backend="filesystem",  # default was "memory", not sure what is more suiting.
    use_temp=True,
    urls_expire_after={
        # "*.github.com": 1000,
        "*": 1000,
    },
)


def download(url: str, headers: dict[str, str] | None = None) -> bytes:
    """Downloads a file from given URL returns its content.

    If the URL is a local path, it is simply read and returned instead.

    Arguments:
        url: URL or local path of the file to use.
        headers: Headers to use for the request.
    """
    logger.debug("Getting file for '%s'", url)
    if parse.urlsplit(url).scheme not in ("http", "https"):
        with pathlib.Path(url).open("rb") as f:
            return f.read()
    if token := os.getenv("GH_TOKEN"):
        gh_header = dict(Authorization=f"token {token}")
    else:
        gh_header = {}
    req = requests.get(url, headers=gh_header | (headers or {}))
    logger.debug("Downloaded %s", url)
    return req.content
