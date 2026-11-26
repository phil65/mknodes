from typing import Any, TYPE_CHECKING

from mknodes.jinja import rendercache
from mknodes.basenodes import mknode
from mknodes.utils import coroutines, resources

if TYPE_CHECKING:
    from collections.abc import Iterator

    from mknodes.jinja.nodeenvironment import RenderResult


class MkTemplateTable(mknode.MkNode):
    """Node for a table showing dependencies for a package."""

    ICON = "material/database"
    REQUIRED_EXTENSIONS = [resources.Extension("tables")]

    def __init__(self, layout: str = "default", **kwargs: Any) -> None:
        self.layout = layout
        super().__init__(**kwargs)

    def iter_items(self) -> Iterator[Any]:
        yield from ()

    def _get_layout(self) -> dict[str, Any]:
        nodefile = self.get_nodefile()
        assert nodefile
        return nodefile._data.get("layouts", {}).get(self.layout)

    def _cells_cache(self) -> tuple[str, dict[tuple[type, bool], list[list[RenderResult]]]]:
        """Cell renders per renderer class and Jinja pass (dropped when the layout changes)."""
        cache = self.__dict__.get("_cells")
        if cache is None or cache[0] != self.layout:
            cache = self.__dict__["_cells"] = (self.layout, {})
        return cache

    async def _render_cells(self) -> list[list[RenderResult]]:
        key = rendercache.cache_key()
        _, by_renderer = self._cells_cache()
        if (cells := by_renderer.get(key)) is not None:
            return cells
        layout = self._get_layout()
        cells = [
            [
                await self.env.render_nodes_async(f"layouts/{self.layout}/{k}", variables=dct)
                for k in layout
            ]
            for dct in self.iter_items()
        ]
        by_renderer[key] = cells
        if self.__dict__.get("_tree_cells", (None,))[0] != self.layout:
            self.__dict__["_tree_cells"] = (self.layout, cells)
        return cells

    async def to_md_unprocessed(self) -> str:
        layout = self._get_layout()
        header = "| " + " | ".join(layout.keys()) + " |"
        divider = "|" + " | ".join(["---"] * len(layout.keys())) + " |"
        text = ""
        for row in await self._render_cells():
            text += "| " + " | ".join(cell.markdown for cell in row) + " |\n"
        return f"{header}\n{divider}\n{text}"

    def get_children(self):
        """Nodes created by the cell templates (of the first render)."""
        tree = self.__dict__.get("_tree_cells")
        if tree is None or tree[0] != self.layout:
            coroutines.run_sync(self._render_cells())
            tree = self.__dict__["_tree_cells"]
        return [child for row in tree[1] for cell in row for child in cell.children]


if __name__ == "__main__":
    table = MkTemplateTable()
