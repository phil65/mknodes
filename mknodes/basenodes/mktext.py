from __future__ import annotations

import logging
import os
import re

from typing import Any, Self

import requests

from mknodes.basenodes import mknode
from mknodes.utils import helpers


logger = logging.getLogger(__name__)

RESPONSE_CODE_OK = 200
EXAMPLE_URL = "https://raw.githubusercontent.com/phil65/mknodes/main/README.md"


def extract_header_section(markdown: str, section_name: str) -> str | None:
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
        self.text = str(text or "")

    def __repr__(self):
        return helpers.get_repr(self, text=self.text)

    def __getitem__(self, section_name: str) -> Self | None:
        markdown = self._to_markdown()
        section_text = extract_header_section(markdown, section_name)
        return None if section_text is None else type(self)(section_text)

    def _to_markdown(self) -> str:
        return self.text if isinstance(self.text, str) else self.text.to_markdown()

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkText("This is the most basic node. It contains `markdown` text")
        page += mknodes.MkReprRawRendered(node, header="### Regular")
        if from_url := MkText.from_url(EXAMPLE_URL):
            page += mknodes.MkReprRawRendered(from_url, header="### From URL")

    @classmethod
    def from_url(cls, url: str) -> Self | None:
        if token := os.getenv("GH_TOKEN"):
            headers = {"Authorization": f"token {token}"}
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url)
        return None if response.status_code != RESPONSE_CODE_OK else cls(response.text)


if __name__ == "__main__":
    section = MkText.from_url(EXAMPLE_URL)
    if section:
        license_section = section["License"]
    print(section)
