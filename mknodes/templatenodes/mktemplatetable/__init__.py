from __future__ import annotations
from typing import Any, TYPE_CHECKING

from mknodes.basenodes import mknode
from mknodes.utils import resources

if TYPE_CHECKING:
    from collections.abc import Iterator


class MkTemplateTable(mknode.MkNode):
    """Node for a table showing dependencies for a package."""

    ICON = "material/database"
    REQUIRED_EXTENSIONS = [resources.Extension("tables")]

    def __init__(self, layout: str = "default", **kwargs: Any) -> None:
        self.layout = layout
        super().__init__(**kwargs)

    def iter_items(self) -> Iterator[Any]:
        yield from ()

    async def _to_markdown(self) -> str:
        nodefile = self.get_nodefile()
        assert nodefile
        layout = nodefile._data.get("layouts", {}).get(self.layout)
        header = "| " + " | ".join(layout.keys()) + " |"
        divider = "|" + " | ".join(["---"] * len(layout.keys())) + " |"
        text = ""
        for dct in self.iter_items():
            strs = [
                await self.env.render_template_async(f"layouts/{self.layout}/{k}", variables=dct)
                for k in layout
            ]
            text += "| " + " | ".join(strs) + " |\n"
        return f"{header}\n{divider}\n{text}"

    @property
    def children(self):
        children = []
        nodefile = self.get_nodefile()
        assert nodefile
        layout = nodefile._data.get("layouts", {}).get(self.layout)
        for dct in self.iter_items():
            for k in layout:
                self.env.render_template(f"layouts/{self.layout}/{k}", variables=dct)
                children += self.env.rendered_children
        return children

    @children.setter
    def children(self, val) -> None:
        pass


if __name__ == "__main__":
    table = MkTemplateTable()
