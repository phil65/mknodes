from __future__ import annotations

import logging
import textwrap

import mkdocs_gen_files

from mknodes import connectionbuilder, node


logger = logging.getLogger(__name__)


class NodeConnectionBuilder(connectionbuilder.ConnectionBuilder):
    def get_children(self, item):
        return item.children

    def get_id(self, item):
        # id() would be enough, but name is sometimes useful for debugging.
        return f"{type(item).__name__}_{id(item)}"

    def get_title(self, item) -> str:
        return f"{type(item).__name__}"


class MkNode(node.BaseNode):
    """Base class for everything which can be expressed as Markup.

    The class inherits from BaseNode. The idea is that starting from the
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
        from mknodes import nav

        parent = self
        parts = [self.section] if isinstance(self, nav.Nav) and self.section else []
        while parent := parent.parent_item:
            if isinstance(parent, nav.Nav) and parent.section:
                parts.append(parent.section)
        return tuple(reversed(parts))

    @property
    def resolved_file_path(self) -> str:
        """Returns the resulting section/subsection/../filename.xyz path."""
        filename = str(self.path) if hasattr(self, "path") else ""
        path = "/".join(self.resolved_parts) + "/" + filename
        return path

    def virtual_files(self):
        """Returns a dict containing the virtual files attached to this tree element.

        This can be overridden by nodes if they want files to be included in the build.
        """
        return {}

    def all_virtual_files(self) -> dict[str, str | bytes]:
        """Return a dictionary containing all virtual files of itself and all children.

        Dict key contains the filename, dict value contains the file content.

        The resulting filepath is determined based on the tree hierarchy.
        """
        from mknodes import nav

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


if __name__ == "__main__":
    section = MkNode(header="fff")
