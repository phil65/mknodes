from __future__ import annotations

from collections.abc import Mapping
import logging

from typing import Any

from mknodes.basenodes import mknode, mktext
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkDefinitionList(mknode.MkNode):
    """Node for definition lists."""

    REQUIRED_EXTENSIONS = ["def_list"]
    ICON = "material/library"

    def __init__(
        self,
        data: dict[str | mknode.MkNode, str | mknode.MkNode] | None = None,
        *,
        header: str = "",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            data: Data show for the table
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header=header, **kwargs)
        match data:
            case Mapping():
                self.data = {
                    k: mktext.MkText(v) if isinstance(v, str) else v
                    for k, v in data.items()
                }
            case None:
                self.data = {}
            case _:
                raise TypeError(data)

    def __repr__(self):
        kwarg_data = {
            k: str(v) if isinstance(v, mktext.MkText) else v for k, v in self.data.items()
        }
        return helpers.get_repr(self, data=kwarg_data)

    @property
    def children(self):
        return list(self.data.values())

    @children.setter
    def children(self, data):
        match data:
            case Mapping():
                self.data = data
            case list():
                self.data = {self.to_item(i): False for i in data}
            case None:
                self.data = {}
            case _:
                raise TypeError(data)

    def to_item(self, i):
        item = mktext.MkText(i) if isinstance(i, str | None) else i
        item.parent = self
        return item

    def _to_markdown(self) -> str:
        result = []
        for k, v in self.data.items():
            lines = str(v).split("\n")
            result.extend([str(k), f":   {lines[0]}"])
            result.extend(f"    {i}" for i in lines[1:])
            result.append("")
        return "\n".join(result) + "\n"

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.status = "new"
        definitions = dict(something="A definition", somethingelse="Another\ndefinition")
        node = MkDefinitionList(data=definitions)
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    ls = MkDefinitionList(data=dict(a="b\nc", c="d"))
    print(ls)
