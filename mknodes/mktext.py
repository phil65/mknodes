from __future__ import annotations

import logging

from mknodes import mknode
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkText(mknode.MkNode):
    """Class for any Markup text.

    All classes inheriting from MkNode can get converted to this Type.
    """

    def __init__(self, text: str | mknode.MkNode = "", header: str = "", parent=None):
        super().__init__(header=header, parent=parent)
        self.text = text

    def __repr__(self):
        return helpers.get_repr(self, text=self.text)

    def _to_markdown(self) -> str:
        return self.text if isinstance(self.text, str) else self.text.to_markdown()


if __name__ == "__main__":
    section = MkText(header="fff")
