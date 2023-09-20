from __future__ import annotations

from collections.abc import Iterable
import re
import time

from typing import TYPE_CHECKING

from mknodes.basenodes import processors
from mknodes.data import datatypes
from mknodes.info import contexts
from mknodes.treelib import node
from mknodes.utils import log, requirements


if TYPE_CHECKING:
    from mknodes import project


logger = log.get_logger(__name__)


HEADER_REGEX = re.compile(r"^(#{1,6}) (.*)")


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
    REQUIRED_EXTENSIONS: list[requirements.Extension] = []
    REQUIRED_PLUGINS: list[requirements.Plugin] = []
    STATUS: datatypes.PageStatusStr | None = None
    CSS: list[requirements.CSSFile | requirements.CSSLink | requirements.CSSText] = []
    JS_FILES: list[requirements.JSLink | requirements.JSFile] = []
    children: list[MkNode]
    _context = contexts.ProjectContext()
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
        self.ctx.env.globals["mknode"] = self
        self.ctx.env.set_mknodes_filters(parent=self)
        return self.ctx.env

    def to_child_node(self, other) -> MkNode:  # type: ignore[return]
        import mknodes

        match other:
            case str() if (match := HEADER_REGEX.match(other)) and "\n" not in other:
                return mknodes.MkHeader(match[2], level=len(match[1]), parent=self)
            case str():
                return mknodes.MkText(other, parent=self)
            case list():
                return mknodes.MkContainer([self.to_child_node(i) for i in other])
            case mknodes.MkNode():
                other.parent = self
                return other
            case _:
                raise TypeError(other)

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

    def get_node_requirements(self) -> requirements.Requirements:
        """Return the requirements specific for this node."""
        extension = {k.extension_name: dict(k) for k in self.REQUIRED_EXTENSIONS}
        return requirements.Requirements(
            js=self.JS_FILES,
            markdown_extensions=extension,
            plugins=self.REQUIRED_PLUGINS,
            css=self.CSS,
        )

    def get_requirements(self) -> requirements.Requirements:
        """Return the "final" requirements object."""
        logger.debug("Collecting requirements from tree...")
        nodes = [*list(self.descendants), self]
        req = requirements.Requirements(markdown_extensions={"pymdownx.emoji": {}})
        for _node in nodes:
            node_req = _node.get_node_requirements()
            req.merge(node_req)
        return req

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

    def to_html(self) -> str:
        """Convert node to HTML using the requirements from node + children."""
        import markdown

        md = self.to_markdown()
        reqs = self.get_requirements()
        configs = reqs.markdown_extensions
        exts = list(configs.keys())
        return markdown.Markdown(extensions=exts, extension_configs=configs).convert(md)


if __name__ == "__main__":
    import mknodes

    section = "pre" >> mknodes.MkText("hello\n# Header\nfdsfds") >> "test" >> "xx"
    print(section)
