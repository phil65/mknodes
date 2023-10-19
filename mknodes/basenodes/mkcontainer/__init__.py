from __future__ import annotations

from collections.abc import Iterator
import contextlib

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


class MkContainer(mknode.MkNode):
    """A base class for Nodes containing other MkNodes."""

    ICON = "material/database"

    def __init__(
        self,
        content: list | None | str | mknode.MkNode = None,
        block_separator: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            content: Child Nodes of this container
            block_separator: Separator to put between blocks. Defaults to 2 linebreaks
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.block_separator = "\n\n" if block_separator is None else block_separator
        match content:
            case None:
                self.items: list[mknode.MkNode] = []
            case str():
                self.items = [self.to_child_node(content)] if content else []
            case mknode.MkNode():
                self.items = [self.to_child_node(content)]
            case list():
                self.items = [self.to_child_node(i) for i in content]
            case _:
                raise TypeError(content)

    def __bool__(self):
        return bool(self.items)

    def __add__(self, other: str | mknode.MkNode):
        self.append(other)
        return self

    def __iter__(self) -> Iterator[mknode.MkNode]:  # type: ignore
        return iter(self.items)

    def __repr__(self):
        content = [reprhelpers.to_str_if_textnode(i) for i in self.items]
        return reprhelpers.get_repr(self, content=content)

    @contextlib.contextmanager
    def in_html_tag(self, tag_name: str, **attributes: Any):
        """Will wrap the content in html tags with tag name.

        Examples:
            with node.in_html_tag("div", **{"class": "css_class"}):
                node += mk.MkSomething()

        Arguments:
            tag_name: Tag to use for wrapping
            attributes: addtional attributes for the XML element
        """
        if attributes:
            attr_txt = " " + " ".join(f"{k!r}={v!r}" for k, v in attributes.items())
        else:
            attr_txt = ""
        text = f"<{tag_name}{attr_txt}>"
        self.append(text)
        container = MkContainer(parent=self)
        yield container
        for item in container:
            self.append(item)
        self.append(f"</{tag_name}>")

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        page += "MkContainers are usually only used as a base class"
        page += "It basically only carries other nodes and stringifies them sequentially."
        item_1 = mk.MkCode(code="a = 1 + 2")
        item_2 = mk.MkText("abc")
        node = MkContainer(content=[item_1, item_2])
        page += mk.MkReprRawRendered(node)

    def _to_markdown(self) -> str:
        return self.block_separator.join(i.to_markdown() for i in self.items)

    def append(self, other: str | mknode.MkNode):
        """Append a MkNode to the end of given MkPage.

        Arguments:
            other: The node / text to append
        """
        node = self.to_child_node(other)
        self.items.append(node)  # type: ignore[arg-type]

    def insert(self, index: int, other: str | mknode.MkNode):
        """Insert a MkNode into desired position of given MkPage.

        Arguments:
            index: Position where node should get inserted
            other: The node / text to insert
        """
        node = self.to_child_node(other)
        self.items.insert(index, node)

    @property  # type: ignore
    def children(self) -> list[mknode.MkNode]:
        return self.items

    @children.setter
    def children(self, children: list[mknode.MkNode]):
        self.items = children


if __name__ == "__main__":
    section = MkContainer(header="fff")
    with section.in_html_tag("ab", c="e"):
        section += "hello"
    print(section)
