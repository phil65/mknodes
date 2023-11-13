from __future__ import annotations
from typing import Any

from jinja2 import filters

from mknodes.basenodes import mkcontainer, mknode
from mknodes.utils import log, xmlhelpers as xml


logger = log.get_logger(__name__)


class MkGrid(mkcontainer.MkContainer):
    """Node for showing a grid."""

    ICON = "material/view-grid"

    def __init__(self, items: list[str | mknode.MkNode] | None = None, **kwargs: Any):
        """Initialize the node.

        Arguments:
            items: The items of this node.
            kwargs: Keyword arguments passed to parent
        """
        match items:
            case None:
                items = []
            case list():
                items = [self.to_child_node(i) for i in items]
        super().__init__(content=items, **kwargs)

    def get_element(self) -> xml.Div:
        root = xml.Div("grid cards", markdown=True)
        if not self.items:
            return root
        result = [f"-   {filters.do_indent(item.to_markdown())}" for item in self.items]
        content = "\n".join(result)
        root.text = "\n\n" + content + "\n"
        return root

    def _to_markdown(self) -> str:
        root = self.get_element()
        return root.to_string(space="")


if __name__ == "__main__":
    import mknodes as mk

    keys = mk.MkKeys(keys="Ctrl+A")
    grid = MkGrid([keys, keys])
    print(grid)
