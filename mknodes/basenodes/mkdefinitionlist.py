from __future__ import annotations

from collections.abc import Mapping
import logging

from typing import Any

from mknodes.basenodes import mkcontainer, mknode
from mknodes.utils import helpers, reprhelpers


logger = logging.getLogger(__name__)


class MkDefinition(mkcontainer.MkContainer):
    """Node for a single definition."""

    REQUIRED_EXTENSIONS = ["def_list"]
    ICON = "material/library"

    def __init__(
        self,
        title: str = "",
        content: list | None | str | mknode.MkNode = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            title: Setting title
            content: Markdown content for this block
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

    def __repr__(self):
        return reprhelpers.get_repr(self, title=self._title, content=self.items)

    def _to_markdown(self) -> str:
        lines = super()._to_markdown().split("\n")
        result = [f"{self.title}", f":   {lines[0]}"]
        result.extend(f"    {i}" for i in lines[1:])
        result.append("")
        return "\n".join(result) + "\n"

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkDefinition("test", content="hfkdlsjk")
        page += mknodes.MkReprRawRendered(node, header="### Regular")


class MkDefinitionList(mkcontainer.MkContainer):
    """Node for definition lists."""

    REQUIRED_EXTENSIONS = ["def_list"]
    ICON = "material/library"

    def __init__(
        self,
        data: Mapping[str | mknode.MkNode, str | mknode.MkNode] | None = None,
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
        kwarg_data = {k: helpers.to_str_if_textnode(v) for k, v in self.data.items()}
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
                self.data = {i: self.to_child_node(item) for i, item in enumerate(data)}
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

    @staticmethod
    def create_example_page(page):
        import mknodes

        definitions = dict(something="A definition", somethingelse="Another\ndefinition")
        node = MkDefinitionList(data=definitions)
        page += mknodes.MkReprRawRendered(node, header="### Regular")

        definitions = dict(admonition=mknodes.MkAdmonition("Nested markup"))
        node = MkDefinitionList(data=definitions)
        page += mknodes.MkReprRawRendered(node, header="### Nested markup")


if __name__ == "__main__":
    ls = MkDefinitionList(data=dict(a="b\nc", c="d"))
    print(ls)
