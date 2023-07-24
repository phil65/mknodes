from __future__ import annotations

import logging
import textwrap

import mkdocs_gen_files

from mknodes import node
from mknodes.utils import connectionbuilder


logger = logging.getLogger(__name__)


class NodeConnectionBuilder(connectionbuilder.ConnectionBuilder):
    def get_children(self, item):
        return item.children

    def get_id(self, item):
        # id() would be enough, but name is sometimes useful for debugging.
        return f"{type(item).__name__}_{id(item)}"

    def get_title(self, item) -> str:
        return f"{type(item).__name__}"


class MkNode(node.Node):
    """Base class for everything which can be expressed as Markup.

    The class inherits from Node. The idea is that starting from the
    root nav (aka Docs) down to nested Markup blocks, the whole project can be represented
    by one tree.

    Arguments:
        header: Optional header for contained Markup
        indent: Indentation of given Markup (unused ATM)
        parent: Parent for building the tree
    """

    def __init__(self, header: str = "", indent: str = "", parent: MkNode | None = None):
        super().__init__(parent=parent)
        self.header = header
        self.indent = indent

    def __str__(self):
        return self.to_markdown()

    # @staticmethod
    # def examples():
    #     yield from ()

    def _to_markdown(self) -> str:
        return NotImplemented

    def to_markdown(self) -> str:
        """Outputs markdown for self and all children."""
        text = self._to_markdown()
        if self.indent:
            text = textwrap.indent(text, self.indent)
        return f"## {self.header}\n\n{text}" if self.header else text

    @property
    def resolved_parts(self) -> tuple[str, ...]:
        """Returns a tuple containing all section names."""
        from mknodes import mknav

        parent = self
        parts = [self.section] if isinstance(self, mknav.MkNav) and self.section else []
        while parent := parent.parent_item:
            if isinstance(parent, mknav.MkNav) and parent.section:
                parts.append(parent.section)
        return tuple(reversed(parts))

    @property
    def resolved_file_path(self) -> str:
        """Returns the resulting section/subsection/../filename.xyz path."""
        filename = str(self.path) if hasattr(self, "path") else ""
        return "/".join(self.resolved_parts) + "/" + filename

    def virtual_files(self):
        """Returns a dict containing the virtual files attached to this tree element.

        This can be overridden by nodes if they want files to be included in the build.
        """
        return {}

    @property
    def resolved_virtual_files(self) -> dict[str, str | bytes]:
        """Return a dict containing all virtual files with resolved file paths."""
        from mknodes import mknav

        sections = [i.section for i in self.ancestors if isinstance(i, mknav.MkNav)]
        section = "/".join(i for i in reversed(sections) if i is not None)
        if section:
            section += "/"
        return {f"{section}{k}": v for k, v in self.virtual_files().items()}

    def all_virtual_files(self, only_children: bool = False) -> dict[str, str | bytes]:
        """Return a dictionary containing all virtual files of itself and all children.

        Dict key contains the filename, dict value contains the file content.

        The resulting filepath is determined based on the tree hierarchy.
        """
        all_files: dict[str, str | bytes] = {}
        for des in self.descendants:
            all_files |= des.resolved_virtual_files
        if not only_children:
            all_files |= self.resolved_virtual_files
        return all_files

    def write(self, only_children: bool = False):
        """Write files to virtual folder.

        Arguments:
            only_children: Whether to exclude self for data.
        """
        # path = pathlib.Path(self.path)
        # path.parent.mkdir(parents=True, exist_ok=True)
        for k, v in self.all_virtual_files(only_children=only_children).items():
            logger.info("Written file to %s", k)
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


if __name__ == "__main__":
    section = MkNode(header="fff")
