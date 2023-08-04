from __future__ import annotations

import logging
import os
import re

import requests

from typing_extensions import Self

from mknodes.basenodes import mknode
from mknodes.utils import helpers


logger = logging.getLogger(__name__)

RESPONSE_CODE_OK = 200
EXAMPLE_URL = "https://raw.githubusercontent.com/phil65/mknodes/main/README.md"


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
        parent: mknode.MkNode | None = None,
    ):
        """Constructor.

        Arguments:
            text: Markup text
            header: Section header
            parent: Node parent
        """
        super().__init__(header=header, parent=parent)
        self.text = str(text or "")

    def __repr__(self):
        return helpers.get_repr(self, text=self.text)

    def __getitem__(self, section_name: str) -> Self | None:
        markdown = self._to_markdown()
        header_pattern = re.compile(f"^(#+) {section_name}$", re.MULTILINE)
        header_match = header_pattern.search(markdown)
        if header_match is None:
            return None
        section_level = len(header_match[1])
        start_index = header_match.span()[1] + 1
        end_pattern = re.compile(f"^#{{2,{section_level}}} ", re.MULTILINE)
        end_match = end_pattern.search(markdown[start_index:])
        if end_match is None:
            return type(self)(markdown[start_index:])
        end_index = end_match.span()[0]
        return type(self)(markdown[start_index : end_index + start_index])

    def _to_markdown(self) -> str:
        return self.text if isinstance(self.text, str) else self.text.to_markdown()

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkText("This is the most basic node. It contains `markdown` text")
        page += mknodes.MkReprRawRendered(node)
        if from_url := MkText.from_url(EXAMPLE_URL):
            page += mknodes.MkReprRawRendered(from_url)

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
