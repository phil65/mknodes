from __future__ import annotations

import collections
import logging
import os
import pathlib
import re

from typing import TYPE_CHECKING
import urllib.parse

from mkdocs.plugins import BasePlugin


if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files
    from mkdocs.structure.pages import Page

logger = logging.getLogger(f"mkdocs.plugins.{__name__}")

# For Regex, match groups are:
#       0: Whole markdown link e.g. [Alt-text](url)
#       1: Alt text
#       2: Full URL e.g. url + hash anchor
#       3: Filename e.g. filename.md
#       4: File extension e.g. .md, .png, etc.
#       5. hash anchor e.g. #my-sub-heading-link
AUTOLINK_RE = r"\[([^\]]+)\]\((([^)/]+\.(md|png|jpg))(#.*)*)\)"


class AutoLinkReplacerPlugin:
    def __init__(self, base_docs_url, page_url, mapping):
        self.mapping = mapping
        self.page_url = page_url
        self.base_docs_url = pathlib.Path(base_docs_url)
        # Absolute URL of the linker
        self.linker_url = os.path.dirname(self.base_docs_url / page_url)  # noqa: PTH120

    def __call__(self, match):
        # Name of the markdown file
        filename = urllib.parse.unquote(match.group(3).strip())
        if filename not in self.mapping:
            return f"`{match.group(3).replace('.md', '')}`"
        filenames = self.mapping[filename]
        # if len(filenames) > 1:
        #     logger.warning(
        #         f"{self.page_url}: {match.group(3)} has multiple targets: {filenames}"
        #     )
        abs_link_url = (self.base_docs_url / filenames[0]).parent
        # need os.replath here bc pathlib.relative_to throws an exception
        # when linking across drives
        rel_path = os.path.relpath(abs_link_url, self.linker_url)
        # html_filename = filename.replace(".md", ".html")
        rel_link_url = os.path.join(rel_path, filename)  # noqa: PTH118
        new_text = (
            match.group(0).replace(match.group(2), rel_link_url)
            if match.group(5) is None
            else match.group(0).replace(match.group(2), rel_link_url + match.group(5))
        )
        new_text = new_text.replace("\\", "/")
        logger.debug(
            "LinkReplacer: %s: %s -> %s",
            self.page_url,
            match.group(3),
            rel_link_url,
        )
        return new_text


class LinkReplacerPlugin(BasePlugin):
    def on_page_markdown(
        self,
        markdown: str,
        *,
        page: Page,
        config: MkDocsConfig,
        files: Files,
    ) -> str | None:
        base_docs_url = config["docs_dir"]
        page_url = page.file.src_path
        mapping = collections.defaultdict(list)
        for file_ in files:
            filename = os.path.basename(file_.abs_src_path)  # noqa: PTH119
            mapping[filename].append(file_.url)
        #     print(file_.url, file_.dest_uri)
        # raise ValueError
        plugin = AutoLinkReplacerPlugin(base_docs_url, page_url, mapping)
        return re.sub(AUTOLINK_RE, plugin, markdown)
