from __future__ import annotations

import logging
import re

from typing import Any, Self

from mknodes.basenodes import mknode
from mknodes.utils import cache, reprhelpers


logger = logging.getLogger(__name__)

RESPONSE_CODE_OK = 200
EXAMPLE_URL = "https://raw.githubusercontent.com/phil65/mknodes/main/README.md"


def extract_header_section(markdown: str, section_name: str) -> str | None:
    """Extract block with given header from markdown."""
    header_pattern = re.compile(f"^(#+) {section_name}$", re.MULTILINE)
    header_match = header_pattern.search(markdown)
    if header_match is None:
        return None
    section_level = len(header_match[1])
    start_index = header_match.span()[1] + 1
    end_pattern = re.compile(f"^#{{2,{section_level}}} ", re.MULTILINE)
    end_match = end_pattern.search(markdown[start_index:])
    if end_match is None:
        return markdown[start_index:]
    end_index = end_match.span()[0]
    return markdown[start_index : end_index + start_index]


class MkText(mknode.MkNode):
    """Class for any Markup text.

    All classes inheriting from MkNode can get converted to this Type.
    """

    ICON = "material/text"

    def __init__(
        self,
        text: str | mknode.MkNode | None = "",
        *,
        header: str = "",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            text: Markup text
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header=header, **kwargs)
        self._text = str(text or "")

    def __repr__(self):
        return reprhelpers.get_repr(self, text=self.text)

    def __getitem__(self, section_name: str) -> Self | None:
        markdown = self._to_markdown()
        section_text = extract_header_section(markdown, section_name)
        return None if section_text is None else type(self)(section_text)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    def _to_markdown(self) -> str:
        return self.text

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkText("This is the most basic node. It contains `markdown` text")
        page += mknodes.MkReprRawRendered(node, header="### Regular")
        if from_url := MkText.from_url(EXAMPLE_URL):
            page += mknodes.MkReprRawRendered(from_url, header="### From URL")

    @classmethod
    def from_url(cls, url: str) -> Self | None:
        """Build a MkText node on a remote markup file.

        If the URL contains a "#" (http://.../markdown.md#section),
        it will try to extract the given section.

        Arguments:
            url: URL to get markdown from.
        """
        if "#" in url:
            url, section = url.split("#")
            text = cache.download_and_cache_url(url, days=1).decode()
            text = extract_header_section(text, section)
        else:
            text = cache.download_and_cache_url(url, days=1).decode()
        return cls(text) if text is not None else None


if __name__ == "__main__":
    section = MkText.from_url(EXAMPLE_URL)
    if section:
        license_section = section["License"]
    print(section)
