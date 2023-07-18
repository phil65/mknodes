from __future__ import annotations

from collections.abc import Iterator
import logging
import textwrap

import mkdocs_gen_files

from markdownizer import connectionbuilder, node, utils


logger = logging.getLogger(__name__)


class NodeConnectionBuilder(connectionbuilder.ConnectionBuilder):
    def get_children(self, item):
        return item.children

    def get_id(self, item):
        # id() would be enough, but name is sometimes useful for debugging.
        return f"{type(item).__name__}_{id(item)}"

    def get_title(self, item) -> str:
        return f"{type(item).__name__}"


class MarkdownNode(node.BaseNode):
    """Base class for everything which can be expressed as Markup.

    The class inherits from BaseNode. The idea is that starting from the
    root nav (aka Docs) down to nested Markup blocks, the whole project can be represented
    by one tree.

    Arguments:
        header: Optional header for contained Markup
        indent: Indentation of given Markup (unused ATM)
        parent: Parent for building the tree
    """

    def __init__(
        self, header: str = "", indent: str = "", parent: MarkdownNode | None = None
    ):
        super().__init__(parent=parent)
        self.header = header
        self.indent = indent

    def __str__(self):
        return self.to_markdown()

    # @staticmethod
    # def examples():
    #     yield from ()

    def _to_markdown(self):
        return NotImplemented

    def to_markdown(self) -> str:
        """Outputs markdown for self and all children."""
        text = self._to_markdown()
        if self.indent:
            text = textwrap.indent(text, self.indent)
        return f"## {self.header}\n\n{text}" if self.header else text

    @property
    def resolved_parts(self) -> tuple[str, ...]:
        from markdownizer import nav

        parent = self
        parts = [self.section] if isinstance(self, nav.Nav) and self.section else []
        while parent := parent.parent_item:
            if isinstance(parent, nav.Nav) and parent.section:
                parts.append(parent.section)
        return tuple(reversed(parts))

    @property
    def resolved_file_path(self) -> str:
        filename = str(self.path) if hasattr(self, "path") else ""
        path = "/".join(self.resolved_parts) + "/" + filename
        return path

    def virtual_files(self):
        """Virtual, this can be overridden by nodes if they want files to be included."""
        return {}

    def all_virtual_files(self) -> dict[str, str | bytes]:
        """Return a dictionary containing all virtual files of itself and all children.

        Dict key contains the filename, dict value contains the file content.

        The resulting filepath is determined based on the tree hierarchy.
        """
        from markdownizer import nav

        dct: dict[str, str | bytes] = {}
        for des in self.descendants:
            sections = [i.section for i in des.ancestors if isinstance(i, nav.Nav)]
            section = "/".join(i for i in reversed(sections) if i is not None)
            if section:
                section += "/"
            files_for_item = {f"{section}{k}": v for k, v in des.virtual_files().items()}
            dct |= files_for_item
        return dct | self.virtual_files()

    def write(self):
        # path = pathlib.Path(self.path)
        # path.parent.mkdir(parents=True, exist_ok=True)
        for k, v in self.all_virtual_files().items():
            logger.info(f"Written file to {k}")
            mode = "w" if isinstance(v, str) else "wb"
            with mkdocs_gen_files.open(k, mode) as file:
                file.write(v)

    def pretty_print(self, _indent: int = 0):
        """PrettyPrint node and its children."""
        text = _indent * "    " + repr(self) + "->" + self.resolved_file_path
        logger.info(text)
        for child_item in self.children:
            child_item.pretty_print(_indent + 1)

    def to_tree_graph(self, orientation: str = "TD") -> str:
        """Returns markdown to display a tree graph of this node and all subnodes.

        Arguments:
            orientation: Orientation of resulting graph
        """
        item_str = NodeConnectionBuilder([self]).get_graph_connection_text()
        text = f"graph {orientation}\n{item_str}"
        return f"```mermaid\n{text}\n```"


class MarkdownContainer(MarkdownNode):
    """A base class for Nodes containing other MarkdownNodes."""

    def __init__(self, items: list | None = None, **kwargs):
        super().__init__(**kwargs)
        self.items: list[MarkdownNode] = []
        for item in items or []:
            self.append(item)  # noqa: PERF402

    def __add__(self, other: str | MarkdownNode):
        self.append(other)
        return self

    def __iter__(self) -> Iterator[MarkdownNode]:  # type: ignore
        return iter(self.items)

    def __repr__(self):
        return utils.get_repr(self, items=self.items)

    @staticmethod
    def examples():
        from markdownizer import code

        yield dict(items=[code.Code(language="py", code="a = 1 + 2"), Text("abc")])

    def _to_markdown(self) -> str:
        return "\n\n".join(i.to_markdown() for i in self.items)

    def append(self, other: str | MarkdownNode):
        other = Text(other, parent=self) if isinstance(other, str) else other
        self.items.append(other)

    @property  # type: ignore
    def children(self) -> list[MarkdownNode]:
        return self.items

    @children.setter
    def children(self, children: list[MarkdownNode]):
        self.items = children


class Text(MarkdownNode):
    """Class for any Markup text.

    All classes inheriting from MarkdownNode can get converted to this Type.
    """

    def __init__(self, text: str | MarkdownNode = "", header: str = "", parent=None):
        super().__init__(header=header, parent=parent)
        self.text = text

    def __repr__(self):
        return utils.get_repr(self, text=self.text)

    def _to_markdown(self) -> str:
        return self.text if isinstance(self.text, str) else self.text.to_markdown()


if __name__ == "__main__":
    section = MarkdownNode(header="fff")
    for example in MarkdownContainer.examples():
        container = MarkdownContainer(**example)
        print(container)
