from __future__ import annotations

from collections.abc import Iterable
import re
import time

from typing import TYPE_CHECKING, Any

from mknodes.basenodes import processors
from mknodes.data import datatypes
from mknodes.info import contexts
from mknodes.treelib import node
from mknodes.utils import log, resources


if TYPE_CHECKING:
    import mknodes as mk

    from mknodes.jinja import environment


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
    REQUIRED_EXTENSIONS: list[resources.Extension] = []
    REQUIRED_PLUGINS: list[resources.Plugin] = []
    STATUS: datatypes.PageStatusStr | None = None
    CSS: list[resources.CSSFile | resources.CSSText] = []
    JS_FILES: list[resources.JSFile] = []
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
        as_html: bool = False,
        project: mk.Project | None = None,
        parent: MkNode | None = None,
    ):
        """Constructor.

        Arguments:
            header: Optional header for contained Markup
            indent: Indentation of given Markup (unused ATM)
            name: An optional unique identifier (allows getting node via MkNode.get_node)
            shift_header_levels: Regex-based header level shifting (adds/removes #-chars)
            css_classes: A sequence of css class names to use for this node
            as_html: Converts node to HTML on stringifying.
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
        self.as_html = as_html
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
        return self.to_html() if self.as_html else self.to_markdown()

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
        import mknodes as mk

        if self.parent or (isinstance(other, mk.MkNode) and other.parent):
            msg = "Can only perform shift when nodes have no parent"
            raise RuntimeError(msg)
        container = mk.MkContainer(parent=self.parent, block_separator=" ")
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
        """The tree context."""
        if self.associated_project:
            return self.associated_project.context
        return self._context

    @property
    def env(self) -> environment.Environment:
        """The node jinja environment."""
        self.ctx.env.globals["mknode"] = self
        self.ctx.env.set_mknodes_filters(parent=self)
        return self.ctx.env

    @property
    def parent_navs(self) -> list[mk.MkNav]:
        """Return a list of parent MkNavs, ordered from root to leaf."""
        import mknodes as mk

        navs = [i for i in self.ancestors if isinstance(i, mk.MkNav)]
        return list(reversed(navs))

    @property
    def parent_page(self) -> mk.MkPage | None:
        import mknodes as mk

        return next((i for i in self.ancestors if isinstance(i, mk.MkPage)), None)

    def to_child_node(self, other: Any):  # type: ignore[return]
        """Convert given nodes / strings to child nodes.

        Either converts text to an MkNode sets parent of node to self.

        Arguments:
            other: The node / string to convert to a child node.
        """
        import mknodes as mk

        match other:
            case str() if (match := HEADER_REGEX.match(other)) and "\n" not in other:
                return mk.MkHeader(match[2], level=len(match[1]), parent=self)
            case str():
                return mk.MkText(other, parent=self)
            case list():
                return mk.MkContainer([self.to_child_node(i) for i in other])
            case mk.MkNode():
                other.parent = self
                return other
            case _:
                raise TypeError(other)

    @classmethod
    def get_node(cls, name: str) -> MkNode:
        """Get a node from name registry."""
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
            processors.AppendCssClassesProcessor(self),
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

    def attach_css_classes(self, text: str) -> str:
        """Attach CSS classes to given markdown in attr-list style.

        Can be reimplemented if non-default behavior is needed.
        Default behavior is appending the css class snippet with a space
        as separator.

        Arguments:
            text: Markdown to annote
        """
        if not self._css_classes:
            return text
        classes = " ".join(f".{kls_name}" for kls_name in self._css_classes)
        text += f" {{: {classes}}}"
        return text

    @property
    def resolved_parts(self) -> tuple[str, ...]:
        """Return a tuple containing all section names."""
        from mknodes.navs import mknav

        parts = [nav.section for nav in self.parent_navs if nav.section]
        if isinstance(self, mknav.MkNav) and self.section:
            parts.append(self.section)
        return tuple(parts)

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

    def get_node_resources(self) -> resources.Resources:
        """Return the resources specific for this node."""
        extension = {k.extension_name: dict(k) for k in self.REQUIRED_EXTENSIONS}
        css_resources: list[resources.CSSType] = []
        for css in self.CSS:
            if isinstance(css, resources.CSSFile) and css.is_local():
                text = self.env.render_template(css.link)
                css_resource = resources.CSSText(text, css.link)
                css_resources.append(css_resource)
            else:
                css_resources.append(css)
        js_resources: list[resources.JSType] = []
        for js_file in self.JS_FILES:
            if isinstance(js_file, resources.JSFile) and js_file.is_local():
                text = self.env.render_template(js_file.link)
                js_resource = resources.JSText(
                    text,
                    js_file.link,
                    defer=js_file.defer,
                    async_=js_file.async_,
                    crossorigin=js_file.crossorigin,
                    typ=js_file.typ,
                    is_library=js_file.is_library,
                )
                js_resources.append(js_resource)
            else:
                js_resources.append(js_file)
        return resources.Resources(
            js=js_resources,
            markdown_extensions=extension,
            plugins=self.REQUIRED_PLUGINS,
            css=css_resources,
        )

    def get_resources(self) -> resources.Resources:
        """Return the "final" resources object."""
        nodes = [*list(self.descendants), self]
        extensions: dict[str, dict] = {
            "attr_list": {},
            "md_in_html": {},
            "pymdownx.emoji": {},
            "pymdownx.magiclink": dict(
                repo_url_shorthand=True,
                user=self.ctx.metadata.repository_username,
                repo=self.ctx.metadata.repository_name,
            ),
        }

        req = resources.Resources(markdown_extensions=extensions)
        for _node in nodes:
            node_req = _node.get_node_resources()
            req.merge(node_req)
        return req

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        # We dont instanciate MkNode directly, so we take a subclass
        # to show some base class functionality

        node = mk.MkText("Intro\n# A header\nOutro")
        node.shift_header_levels = 2
        page += mk.MkReprRawRendered(node, header="### Shift header levels")

        node = mk.MkText("Every node can also append annotations (1)")
        node.annotations[1] = "Nice!"
        page += mk.MkReprRawRendered(node, header="### Append annotations")

    @property
    def associated_project(self) -> mk.Project | None:
        if proj := self._associated_project:
            return proj
        for ancestor in self.ancestors:
            if proj := ancestor._associated_project:
                return proj
        return None

    @associated_project.setter
    def associated_project(self, value: mk.Project):
        self._associated_project = value

    @classmethod
    def with_default_context(cls, *args, **kwargs):
        import mknodes

        proj = mknodes.Project.for_mknodes()
        return cls(*args, **kwargs, project=proj)

    def to_html(self) -> str:
        """Convert node to HTML using the resources from node + children."""
        import markdown

        md = self.to_markdown()
        reqs = self.get_resources()
        configs = reqs.markdown_extensions
        exts = list(configs.keys())
        return markdown.Markdown(extensions=exts, extension_configs=configs).convert(md)


if __name__ == "__main__":
    import mknodes

    section = "pre" >> mknodes.MkText("hello\n# Header\nfdsfds") >> "test" >> "xx"
    print(section)
