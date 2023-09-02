"""Link replacer."""

from __future__ import annotations

import collections
import os
import re
import urllib.parse

from mkdocs.plugins import get_plugin_logger


logger = get_plugin_logger(__name__)


# For Regex, match groups are:
#       0: Whole markdown link e.g. [Alt-text](url)
#       1: Alt text
#       2: Full URL e.g. url + hash anchor
#       3: Filename e.g. filename.md
#       4: File extension e.g. .md, .png, etc.
#       5. hash anchor e.g. #my-sub-heading-link
AUTOLINK_RE = r"\[([^\]]+)\]\((([^)/]+\.(md|png|jpg))(#.*)*)\)"


def relative_url(url_a: str, url_b: str) -> str:
    """Compute the relative path from URL A to URL B.

    Arguments:
        url_a: URL A.
        url_b: URL B.

    Returns:
        The relative URL to go from A to B.
    """
    parts_a = url_a.split("/")
    if "#" in url_b:
        url_b, anchor = url_b.split("#", 1)
    else:
        anchor = None
    parts_b = url_b.split("/")

    # remove common left parts
    while parts_a and parts_b and parts_a[0] == parts_b[0]:
        parts_a.pop(0)
        parts_b.pop(0)

    # go up as many times as remaining a parts' depth
    levels = len(parts_a) - 1
    parts_relative = [".."] * levels + parts_b
    relative = "/".join(parts_relative)
    return f"{relative}#{anchor}" if anchor else relative


class LinkReplacer:
    def __init__(self):
        self.mapping = collections.defaultdict(list)
        self.page_url = None

    def __call__(self, match):
        filename = urllib.parse.unquote(match.group(3).strip())
        if filename not in self.mapping:
            return f"`{match.group(1)}`"
        filenames = self.mapping[filename]
        if len(filenames) > 1:
            text = "%s: %s has multiple targets: %s"
            logger.debug(text, self.page_url, match.group(3), filenames)
        new_link = relative_url(self.page_url, filenames[0])
        new_text = match.group(0).replace(match.group(2), new_link)
        # new_text = new_text.replace("\\", "/")
        text = "LinkReplacer: %s: %s -> %s"
        logger.debug(text, self.page_url, match.group(3), new_text)
        return new_text

    def add_files(self, files):
        for file_ in files:
            filename = os.path.basename(file_.abs_src_path)  # noqa: PTH119
            url = urllib.parse.unquote(file_.src_uri)
            self.mapping[filename].append(url)

    def replace(self, markdown: str, uri: str) -> str:
        if uri.endswith("SUMMARY.md"):
            return markdown
        self.page_url = uri
        return re.sub(AUTOLINK_RE, self, markdown)
