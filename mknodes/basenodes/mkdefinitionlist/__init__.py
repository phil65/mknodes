from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from jinja2 import filters
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
        self.title = title

    def _to_markdown(self) -> str:
        text = super()._to_markdown()
        return f"{self.title}\n:   {filters.do_indent(text)}\n"


class MkDefinitionList(mkcontainer.MkContainer):
    """Node for definition lists."""

    REQUIRED_EXTENSIONS = [resources.Extension("def_list")]
    ICON = "material/library"

    def __init__(self, data: Mapping | None = None, **kwargs: Any):
        """Constructor.

        Arguments:
            data: Data show for the table
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.data: dict[str, str | mknode.MkNode] = {}
        self.items = data

    def __repr__(self):
        kws = {k: reprhelpers.to_str_if_textnode(v) for k, v in self.data.items()}
        return reprhelpers.get_repr(self, data=kws)

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
        items = [f"{k}\n:   {filters.do_indent(str(v))}\n" for k, v in self.data.items()]
        return "".join(items)


if __name__ == "__main__":
    ls = MkDefinitionList(data=dict(a="b\nc", c="d"))
    print(ls)
