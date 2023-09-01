from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mkcontainer, mknode
from mknodes.utils import reprhelpers


logger = logging.getLogger(__name__)


class MkTask(mkcontainer.MkContainer):
    """Node for a single definition."""

    REQUIRED_EXTENSIONS = ["pymdownx.tasklist"]
    ICON = "material/library"

    def __init__(
        self,
        value: bool = False,
        content: list | None | str | mknode.MkNode = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            value: Setting value
            content: Markdown content for this block
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(content=content, **kwargs)
        self.value = value

    def __repr__(self):
        return reprhelpers.get_repr(self, value=self.value, content=self.items)

    def _to_markdown(self) -> str:
        lines = super()._to_markdown().split("\n")
        val = "x" if self.value else " "
        result = [f"- [{val}] {lines[0]}"]
        result.extend(f"      {i}" for i in lines[1:])
        return "\n".join(result) + "\n"


class MkTaskList(mkcontainer.MkContainer):
    """Node for definition lists."""

    REQUIRED_EXTENSIONS = ["pymdownx.tasklist"]
    ICON = "material/library"

    def __init__(
        self,
        content: list | None | str | mknode.MkNode = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            content: Data show for the table
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(content=content, block_separator="", **kwargs)

    def add_item(self, content, value):
        item = MkTask(value, content)
        self.append(item)

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkTaskList()
        node.add_item("True!", True)
        node.add_item("False!", False)
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    ls = MkTaskList()
    ls.add_item("True", True)
    ls.add_item("False", False)
    print(ls)
