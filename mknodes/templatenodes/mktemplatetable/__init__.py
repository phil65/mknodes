from __future__ import annotations

from mknodes.basenodes import mknode
from mknodes.utils import resources


class MkTemplateTable(mknode.MkNode):
    """Node for a table showing dependencies for a package."""

    ICON = "material/database"
    REQUIRED_EXTENSIONS = [resources.Extension("tables")]

    def __init__(self, layout: str = "default", **kwargs):
        self.layout = layout
        super().__init__(**kwargs)

    def iter_items(self):
        yield from ()

    def _to_markdown(self) -> str:
        layout = self.nodefile._data.get("layouts").get(self.layout)
        header = "| " + " | ".join(layout.keys()) + " |"
        divider = "|" + " | ".join(["---"] * len(layout.keys())) + " |"
        text = ""
        for dct in self.iter_items():
            strs = [
                self.env.render_template(f"layouts/{self.layout}/{k}", variables=dct)
                for k in layout
            ]
            text += "| " + " | ".join(strs) + " |\n"
        return f"{header}\n{divider}\n{text}"

    @property
    def children(self):
        children = []
        layout = self.nodefile._data.get("layouts").get(self.layout)
        for dct in self.iter_items():
            for k in layout:
                self.env.render_template(f"layouts/{self.layout}/{k}", variables=dct)
                children += self.env.rendered_children
        return children

    @children.setter
    def children(self, val):
        pass


if __name__ == "__main__":
    table = MkTemplateTable()
