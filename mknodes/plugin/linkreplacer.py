"""The Mkdocs Plugin."""

from __future__ import annotations

# Partly based on mkdocs-gen-files
import logging
import os
import pathlib
import re
import urllib.parse


try:
    from mkdocs.plugins import get_plugin_logger

    logger = get_plugin_logger(__name__)
except ImportError:
    # TODO: remove once support for MkDocs <1.5 is dropped
    logger = logging.getLogger(f"mkdocs.plugins.{__name__}")  # type: ignore[assignment]


# For Regex, match groups are:
#       0: Whole markdown link e.g. [Alt-text](url)
#       1: Alt text
#       2: Full URL e.g. url + hash anchor
#       3: Filename e.g. filename.md
#       4: File extension e.g. .md, .png, etc.
#       5. hash anchor e.g. #my-sub-heading-link
AUTOLINK_RE = r"\[([^\]]+)\]\((([^)/]+\.(md|png|jpg))(#.*)*)\)"


class LinkReplacer:
    def __init__(self, base_docs_url: str, page_url: str, mapping: dict[str, list[str]]):
        self.mapping = mapping
        self.page_url = page_url
        self.base_docs_url = pathlib.Path(base_docs_url)
        # Absolute URL of the linker
        self.linker_url = os.path.dirname(self.base_docs_url / page_url)  # noqa: PTH120

    def __call__(self, match):
        filename = urllib.parse.unquote(match.group(3).strip())
        if filename not in self.mapping:
            return f"`{match.group(3).replace('.md', '')}`"
        filenames = self.mapping[filename]
        if len(filenames) > 1:
            text = "%s: %s has multiple targets: %s"
            logger.debug(text, self.page_url, match.group(3), filenames)
        abs_link_url = (self.base_docs_url / filenames[0]).parent
        # need os.replath here bc pathlib.relative_to throws an exception
        # when linking across drives
        rel_path = os.path.relpath(abs_link_url, self.linker_url)
        rel_link_url = os.path.join(rel_path, filename)  # noqa: PTH118
        new_text = match.group(0).replace(match.group(2), rel_link_url)
        to_replace_with = rel_link_url + (match.group(5) or "")
        new_text = match.group(0).replace(match.group(2), to_replace_with)
        new_text = new_text.replace("\\", "/")
        text = "LinkReplacer: %s: %s -> %s"
        logger.debug(text, self.page_url, match.group(3), rel_link_url)
        return new_text

    def replace(self, markdown: str) -> str:
        return re.sub(AUTOLINK_RE, self, markdown)
