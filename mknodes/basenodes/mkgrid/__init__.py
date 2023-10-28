from __future__ import annotations
from typing import Any

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
        result = []
        for item in self.items:
            item_str = item.to_markdown()
            lines = item_str.split("\n")
            result += [f"-   {lines[0]}"]
            result.extend(f"    {i}" for i in lines[1:])
        content = "\n".join(result)
        root.text = "\n\n" + content + "\n"
        return root

    def _to_markdown(self) -> str:
        root = self.get_element()
        return root.to_string(space="")

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        # only works for Mkdocs-material sponsors.
        ls = ["Item 1", "Item 2", "Item 3"]
        item_1 = mk.MkList(ls)
        item_2 = mk.MkKeys(keys=["Ctrl+A"])
        grid = MkGrid([item_1, item_2])
        page += mk.MkReprRawRendered(grid)


if __name__ == "__main__":
    import mknodes as mk

    keys = mk.MkKeys(keys="Ctrl+A")
    grid = MkGrid([keys, keys])
    print(grid)
