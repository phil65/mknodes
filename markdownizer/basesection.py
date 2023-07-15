from __future__ import annotations

import logging

import mkdocs_gen_files

from markdownizer import node, utils


logger = logging.getLogger(__name__)


class MarkdownNode(node.BaseNode):
    """Base class for everything which can be expressed as Markup.

    The class inherits from BaseNode. The idea is that starting from the
    root nav (aka Docs) down to nested Markup blocks, the whole project can be represented
    by one tree.
    """

    def __init__(self, header: str = "", parent: MarkdownNode | None = None):
        super().__init__(parent=parent)
        self.header = header

    def __str__(self):
        return self.to_markdown()

    def to_markdown(self):
        """Outputs markdown for self and all children."""
        text = self._to_markdown() + "\n"
        return f"## {self.header}\n\n{text}" if self.header else text

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
            section = "/".join(i for i in sections if i is not None)
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


class Code(Text):
    """Class representing a Code block."""

    def __init__(
        self,
        language: str,
        text: str | MarkdownNode = "",
        *,
        title: str = "",
        header: str = "",
        linenums: int | None = None,
        highlight_lines: list[int] | None = None,
        parent=None,
    ):
        super().__init__(text, header=header, parent=parent)
        self.language = language
        self.title = title
        self.linenums = linenums
        self.highlight_lines = highlight_lines

    def _to_markdown(self) -> str:
        title = f" title={self.title}" if self.title else ""
        return f"```{self.language}{title}\n{self.text}\n```"


if __name__ == "__main__":
    section = MarkdownNode(header="fff")
    section.to_markdown()
