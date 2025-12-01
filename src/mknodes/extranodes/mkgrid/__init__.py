from __future__ import annotations
from typing import Any, TYPE_CHECKING

from jinja2 import filters

from mknodes.basenodes import mkcontainer
from mknodes.utils import log, xmlhelpers as xml

if TYPE_CHECKING:
    from mknodes.basenodes import mknode


logger = log.get_logger(__name__)


class MkGrid(mkcontainer.MkContainer):
    """Node for showing a grid."""

    ICON = "material/view-grid"

    def __init__(self, items: list[str | mknode.MkNode] | None = None, **kwargs: Any) -> None:
        """Initialize the node.

        Args:
            items: The items of this node.
            kwargs: Keyword arguments passed to parent
        """
        match items:
            case None:
                items = []
            case list():
                items = [self.to_child_node(i) for i in items]
        super().__init__(content=items, **kwargs)

    async def get_element(self) -> xml.Div:
        root = xml.Div("grid cards", markdown=True)
        items = self.get_items()
        if not items:
            return root
        result = [f"-   {filters.do_indent(await item.to_markdown())}" for item in items]
        content = "\n".join(result)
        root.text = "\n\n" + content + "\n"
        return root

    async def to_md_unprocessed(self) -> str:
        root = await self.get_element()
        return root.to_string(space="")


if __name__ == "__main__":
    import mknodes as mk

    keys = mk.MkKeys(keys="Ctrl+A")
    grid = MkGrid([keys, keys])
    print(grid)
