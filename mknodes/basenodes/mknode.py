from __future__ import annotations

from collections.abc import Iterable
import time

from typing import TYPE_CHECKING

from mknodes import paths
from mknodes.basenodes import processors
from mknodes.data import datatypes
from mknodes.info import contexts
from mknodes.jinja import environment
from mknodes.pages import pagetemplate
from mknodes.treelib import node
from mknodes.utils import jinjahelpers, log, mergehelpers, requirements


if TYPE_CHECKING:
    from mknodes import project


logger = log.get_logger(__name__)


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
    _context = contexts.ProjectContext()
    _env = environment.Environment(undefined="strict", load_templates=True)
    _name_registry: dict[str, MkNode] = dict()

    def __init__(
        self,
        *,
        header: str = "",
        indent: str = "",
        name: str | None = None,
        shift_header_levels: int = 0,
        css_classes: Iterable[str] | None = None,
        project: project.Project | None = None,
        parent: MkNode | None = None,
    ):
        """Constructor.

        Arguments:
            header: Optional header for contained Markup
            indent: Indentation of given Markup (unused ATM)
            name: An optional unique identifier (allows getting node via MkNode.get_node)
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
        self._node_name = name
        if name is not None:
            self._name_registry[name] = self
        self.stats = contexts.NodeBuildStats()
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

    @property
    def ctx(self):
        if self.associated_project:
            return self.associated_project.context
        return self._context

    @property
    def env(self):
        self._env.globals["parent"] = self.parent
        self._env.set_mknodes_filters(parent=self)
        return self._env

    @classmethod
    def get_node(cls, name: str):
        return cls._name_registry[name]

    def _to_markdown(self) -> str:
        return NotImplemented

    def to_markdown(self) -> str:
        """Outputs markdown for self and all children."""
        now = time.perf_counter()
        text = self._to_markdown()
        for proc in self.get_processors():
            text = proc.run(text)
        self.stats.render_duration = now - time.perf_counter()
        self.stats.render_count += 1
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
        from mknodes.navs import mknav

        node = self
        parts = [self.section] if isinstance(self, mknav.MkNav) and self.section else []
        while node := node.parent:
            if isinstance(node, mknav.MkNav) and node.section:
                parts.append(node.section)
        return tuple(reversed(parts))

    @property
    def files(self):
        """Return a dict containing the virtual files attached to this tree element.

        This can be overridden by nodes if they want files to be included dynamically.
        For static files, use `add_file`.
        """
        return self._files

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

    def get_requirements(self, recursive: bool = True) -> requirements.Requirements:
        all_templates: list[pagetemplate.PageTemplate] = []
        all_js_files: set[str] = set()
        all_plugins: set[str] = set()
        all_extensions: list[dict] = [{"pymdownx.emoji": {}}]
        all_css: set[str] = set()
        logger.debug("Collecting requirements from tree...")
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
            if extension:
                all_extensions.append(extension)
            if js := des.JS:
                if isinstance(js, list):
                    all_js_files.update(js)
                else:
                    all_js_files.add(js)
            for p in des.REQUIRED_PLUGINS:
                all_plugins.add(p)
            if css := des.CSS:
                file_path = paths.RESOURCES / css
                text = file_path.read_text()
                all_css.add(text)
        logger.debug(
            "Collected %s templates, %s js files, %s markdown extensions, %s css blocks",
            len(all_templates),
            len(all_js_files),
            len(all_extensions),
            len(all_css),
        )
        logger.debug("Merging Extensions...")
        all_extensions = mergehelpers.merge_extensions(all_extensions)
        logger.debug("Resulting extensions: %s", len(all_extensions))
        logger.debug("Building Requirements object...")
        return requirements.Requirements(
            templates=all_templates,
            js_files={p: (paths.RESOURCES / p).read_text() for p in all_js_files},
            markdown_extensions=mergehelpers.merge_dicts(*all_extensions),
            plugins=all_plugins,
            css={"mknodes_nodes.css": "\n".join(all_css)},
        )

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

    @classmethod
    def with_default_context(cls, *args, **kwargs):
        import mknodes

        proj = mknodes.Project.for_mknodes()
        return cls(*args, **kwargs, project=proj)


jinjahelpers.set_markdown_exec_namespace(MkNode._env.globals)


if __name__ == "__main__":
    import mknodes

    section = "pre" >> mknodes.MkText("hello\n# Header\nfdsfds") >> "test" >> "xx"
    print(section)
