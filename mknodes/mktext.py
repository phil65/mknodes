from __future__ import annotations

import logging
import re

from typing_extensions import Self

from mknodes import mknode
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkText(mknode.MkNode):
    """Class for any Markup text.

    All classes inheriting from MkNode can get converted to this Type.
    """

    def __init__(
        self,
        text: str | mknode.MkNode = "",
        *,
        header: str = "",
        parent=None,
    ):
        super().__init__(header=header, parent=parent)
        self.text = text

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


if __name__ == "__main__":
    section = MkText(header="fff")
