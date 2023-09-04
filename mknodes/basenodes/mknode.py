from __future__ import annotations

from collections.abc import Iterable
import logging

from typing import TYPE_CHECKING

import mergedeep

from mknodes import paths
from mknodes.basenodes import processors
from mknodes.data import datatypes
from mknodes.pages import pagetemplate
from mknodes.treelib import node
from mknodes.utils import requirements


if TYPE_CHECKING:
    from mknodes import project


logger = logging.getLogger(__name__)


class MkNode(node.Node):
    """Base class for everything which can be expressed as Markup.

    The class inherits from Node. The idea is that starting from the
    root nav (aka Docs) down to nested Markup blocks, the whole project can be represented
    by one tree.

    MkNode is the base class for all nodes. We dont instanciate it directly.
    All subclasses carry an MkAnnotations node (except the MkAnnotations node itself)
    They can also pass an `indent` as well as a `shift_header_levels` keyword argument
    in order to modify the resulting markdown.
    """

    # METADATA (should be set by subclasses)

    ICON = "material/puzzle-outline"
    REQUIRED_EXTENSIONS: list[str] | dict[str, dict] = []
    REQUIRED_PLUGINS: list[str] = []
    STATUS: datatypes.PageStatusStr | None = None
    CSS = None
    JS = None
    children: list[MkNode]

    def __init__(
        self,
        *,
        header: str = "",
        indent: str = "",
        shift_header_levels: int = 0,
        css_classes: Iterable[str] | None = None,
        project: project.Project | None = None,
        parent: MkNode | None = None,
    ):
        """Constructor.

        Arguments:
            header: Optional header for contained Markup
            indent: Indentation of given Markup (unused ATM)
            shift_header_levels: Regex-based header level shifting (adds/removes #-chars)
            css_classes: A sequence of css class names to use for this node
            project: Project this Nav is connected to.
            parent: Parent for building the tree
        """
        super().__init__(parent=parent)
        self.header = header
        self.indent = indent
        self.shift_header_levels = shift_header_levels
        self._files: dict[str, str | bytes] = {}
        self._css_classes: set[str] = set(css_classes or [])
        self._associated_project = project
        # ugly, but convenient.
        from mknodes.basenodes import mkannotations

        if not isinstance(self, mkannotations.MkAnnotations):
            self.annotations = mkannotations.MkAnnotations(parent=self)
        else:
            self.annotations = None

    def __str__(self):
        return self.to_markdown()

    def __hash__(self):
        return hash(self.to_markdown())

    def __eq__(self, other):
        if not type(other) == type(self):
            return False
        dct_1 = self.__dict__.copy()
        dct_1.pop("_parent")
        # dct_1.pop("_annotations")
        dct_2 = other.__dict__.copy()
        dct_2.pop("_parent")
        # dct_2.pop("_annotations")
        return dct_1 == dct_2

    def __rshift__(self, other, inverse: bool = False):
        import mknodes

        if self.parent or (isinstance(other, mknodes.MkNode) and other.parent):
            msg = "Can only perform shift when nodes have no parent"
            raise RuntimeError(msg)
        container = mknodes.MkContainer(parent=self.parent, block_separator=" ")
        if inverse:
            container.append(other)
            container.append(self)
        else:
            container.append(self)
            container.append(other)
        return container

    def __rrshift__(self, other):
        return self.__rshift__(other, inverse=True)

    def _to_markdown(self) -> str:
        return NotImplemented

    def to_markdown(self) -> str:
        """Outputs markdown for self and all children."""
        text = self._to_markdown()
        for proc in self.get_processors():
            text = proc.run(text)
        return text

    def get_processors(self) -> list[processors.TextProcessor]:
        """Return list of processors used to created markdown."""
        return [
            processors.ShiftHeaderLevelProcessor(self.shift_header_levels),
            processors.IndentationProcessor(self.indent),
            processors.AppendCssClassesProcessor(self._css_classes),
            processors.PrependHeaderProcessor(self.header),
            processors.AnnotationProcessor(self),
        ]

    def attach_annotations(self, text: str) -> str:
        """Attach annotations block to given markdown.

        Can be reimplemented if non-default annotations are needed.

        Arguments:
            text: Markdown to annote
        """
        return self.annotations.annotate_text(text) if self.annotations else text

    @property
    def resolved_parts(self) -> tuple[str, ...]:
        """Return a tuple containing all section names."""
        from mknodes import mknav

        node = self
        parts = [self.section] if isinstance(self, mknav.MkNav) and self.section else []
        while node := node.parent:
            if isinstance(node, mknav.MkNav) and node.section:
                parts.append(node.section)
        return tuple(reversed(parts))

    def virtual_files(self):
        """Return a dict containing the virtual files attached to this tree element.

        This can be overridden by nodes if they want files to be included dynamically.
        For static files, use `add_file`.
        """
        return self._files

    @property
    def resolved_virtual_files(self) -> dict[str, str | bytes]:
        """Return a dict containing all virtual files with resolved file paths."""
        from mknodes import mknav

        sections = [i.section for i in self.ancestors if isinstance(i, mknav.MkNav)]
        section = "/".join(i for i in reversed(sections) if i is not None)
        if section:
            section += "/"
        return {f"{section}{k}": v for k, v in self.virtual_files().items()}

    def add_file(self, filename: str, data: str | bytes):
        """Add a static file as data to this node.

        Arguments:
            filename: Filename of the file to add
            data: Data of the file
        """
        self._files[filename] = data

    def add_css_class(self, class_name: str):
        """Wrap node markdown with given css class.

        Arguments:
            class_name: CSS class to wrap the node with
        """
        self._css_classes.add(class_name)

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

    def get_requirements(self, recursive: bool = True) -> requirements.Requirements:
        all_templates: list[pagetemplate.PageTemplate] = []
        all_js_files: set[str] = set()
        all_plugins: set[str] = set()
        all_extensions: list[dict] = [{"pymdownx.emoji": {}}]
        all_css: set[str] = set()
        nodes = [*list(self.descendants), self] if recursive else [self]
        for des in nodes:
            if hasattr(des, "template") and isinstance(
                des.template,
                pagetemplate.PageTemplate,
            ):
                all_templates.append(des.template)
            extension = (
                des.REQUIRED_EXTENSIONS
                if isinstance(des.REQUIRED_EXTENSIONS, dict)
                else {k: {} for k in des.REQUIRED_EXTENSIONS}
            )
            all_extensions.append(extension)
            if js := des.JS:
                if isinstance(js, list):
                    all_js_files.update(js)
                else:
                    all_js_files.add(js)
            for p in des.REQUIRED_PLUGINS:
                all_plugins.add(p)
            if css := des.get_css():
                all_css.add(css)
        return requirements.Requirements(
            templates=all_templates,
            js_files={p: (paths.RESOURCES / p).read_text() for p in all_js_files},
            markdown_extensions=mergedeep.merge(*all_extensions),
            plugins=all_plugins,
            css={"mknodes_nodes.css": "\n".join(all_css)},
        )

    def get_css(self) -> str | None:
        """Get css used by this node."""
        if not self.CSS:
            return None
        file_path = paths.RESOURCES / self.CSS
        return file_path.read_text()

    @staticmethod
    def create_example_page(page):
        import mknodes

        # We dont instanciate MkNode directly, so we take a subclass
        # to show some base class functionality

        node = mknodes.MkText("Intro\n# A header\nOutro")
        node.shift_header_levels = 2
        page += mknodes.MkReprRawRendered(node, header="### Shift header levels")

        node = mknodes.MkText("Every node can also append annotations (1)")
        node.annotations[1] = "Nice!"
        page += mknodes.MkReprRawRendered(node, header="### Append annotations")

    @property
    def associated_project(self) -> project.Project | None:
        if proj := self._associated_project:
            return proj
        for ancestor in self.ancestors:
            if proj := ancestor._associated_project:
                return proj
        return None

    @associated_project.setter
    def associated_project(self, value: project.Project):
        self._associated_project = value


if __name__ == "__main__":
    import mknodes

    section = "pre" >> mknodes.MkText("hello\n# Header\nfdsfds") >> "test" >> "xx"
    print(section)
    print(section.get_requirements())
