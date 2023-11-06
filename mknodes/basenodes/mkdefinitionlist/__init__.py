from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from mknodes.basenodes import mkcontainer, mknode
from mknodes.utils import log, reprhelpers, resources


logger = log.get_logger(__name__)


class MkDefinition(mkcontainer.MkContainer):
    """Node for a single definition."""

    REQUIRED_EXTENSIONS = [resources.Extension("def_list")]
    ICON = "material/library"

    def __init__(
        self,
        content: list | None | str | mknode.MkNode = None,
        title: str = "",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            content: Markdown content for this block
            title: Setting title
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(content=content, **kwargs)
        self._title = title

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    def _to_markdown(self) -> str:
        lines = super()._to_markdown().split("\n")
        result = [f"{self.title}", f":   {lines[0]}"]
        result.extend(f"    {i}" for i in lines[1:])
        result.append("")
        return "\n".join(result) + "\n"

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkDefinition("hfkdlsjk", title="test")
        page += mk.MkReprRawRendered(node, header="### Regular")


class MkDefinitionList(mkcontainer.MkContainer):
    """Node for definition lists."""

    REQUIRED_EXTENSIONS = [resources.Extension("def_list")]
    ICON = "material/library"

    def __init__(
        self,
        data: Mapping | None = None,
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
        self.data: dict[str, str | mknode.MkNode] = {}
        self.items = data

    def __repr__(self):
        kwarg_data = {k: reprhelpers.to_str_if_textnode(v) for k, v in self.data.items()}
        return reprhelpers.get_repr(self, data=kwarg_data)

    @property
    def items(self):
        return list(self.data.values())

    @items.setter
    def items(self, data):
        match data:
            case Mapping():
                self.data = {k: self.to_child_node(v) for k, v in data.items()}
            case list():
                self.data = {
                    str(i): self.to_child_node(item) for i, item in enumerate(data)
                }
            case None:
                self.data = {}
            case _:
                raise TypeError(data)

    def _to_markdown(self) -> str:
        result = []
        for k, v in self.data.items():
            lines = str(v).split("\n")
            result.extend([str(k), f":   {lines[0]}"])
            result.extend(f"    {i}" for i in lines[1:])
            result.append("")
        return "\n".join(result) + "\n"

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        defs_1 = dict(something="A definition", somethingelse="Another\ndefinition")
        node = MkDefinitionList(data=defs_1)
        page += mk.MkReprRawRendered(node, header="### Regular")

        defs_2 = dict(admonition=mk.MkAdmonition("Nested markup"))
        node = MkDefinitionList(data=defs_2)
        page += mk.MkReprRawRendered(node, header="### Nested markup")


if __name__ == "__main__":
    ls = MkDefinitionList(data=dict(a="b\nc", c="d"))
    print(ls)
