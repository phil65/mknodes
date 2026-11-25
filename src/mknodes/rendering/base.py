"""Renderer base class: turns nodes into the Markdown of one flavour.

A renderer is a registry of rules (node type -> render function) for one Markdown
flavour. Nodes without a rule render themselves (`get_content()` /
`to_md_unprocessed()`), which produces Material for MkDocs flavoured Markdown.

The active renderer is stored in a context variable, so nested nodes, Jinja templates
(`{{ node }}`) and `str(node)` all render in the same flavour.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import contextlib
import contextvars
from typing import TYPE_CHECKING, Any, ClassVar

from mknodes.utils import log, resources


if TYPE_CHECKING:
    from collections.abc import Generator

    import mknodes as mk
    from mknodes.basenodes import mknode, processors
    from mknodes.build.output import BuildOutput


logger = log.get_logger(__name__)

# Render function: `async def rule(node, renderer) -> str` (unprocessed Markdown).
type Rule = Callable[[Any, Renderer], Awaitable[str]]


class Renderer:
    """Renders nodes as Markdown of one flavour.

    Subclass it for a new flavour and register rules with the `rule` decorator.
    Rule lookup walks the node class hierarchy: a rule for `MkBlock` also renders
    `MkDetailsBlock`, unless a class in between renders itself (defines
    `get_content` / `to_md_unprocessed`) and has no rule of its own.
    Rules of parent renderer classes are inherited.
    """

    name: ClassVar[str] = "markdown"
    """Flavour name."""
    template_key: ClassVar[str | None] = None
    """`[output.<key>]` section of node files whose template serves as a rule."""
    _rules: ClassVar[dict[type, Rule]] = {}
    _lookup_cache: ClassVar[dict[tuple[type[Renderer], type], Rule | None]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._rules = {}

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    @classmethod
    def rule[R: Rule](cls, *node_types: type) -> Callable[[R], R]:
        """Decorator registering a render function for given node types."""

        def decorator(fn: R) -> R:
            for node_type in node_types:
                cls._rules[node_type] = fn
            Renderer._lookup_cache.clear()
            return fn

        return decorator

    @classmethod
    def find_rule(cls, node_type: type) -> Rule | None:
        """Return the rule for given node type (None: the node renders itself)."""
        key = (cls, node_type)
        if key not in Renderer._lookup_cache:
            Renderer._lookup_cache[key] = cls._find_rule(node_type)
        return Renderer._lookup_cache[key]

    @classmethod
    def _find_rule(cls, node_type: type) -> Rule | None:
        from mknodes.basenodes import mknode

        renderers = [r for r in cls.__mro__ if issubclass(r, Renderer)]
        for klass in node_type.__mro__:
            if not issubclass(klass, mknode.MkNode):
                break
            for renderer in renderers:
                if klass in renderer._rules:
                    return renderer._rules[klass]
            if template_rule := _get_template_rule(klass, renderers):
                return template_rule
            if "get_content" in klass.__dict__ or "to_md_unprocessed" in klass.__dict__:
                return None
        return None

    @classmethod
    def supports(cls, node_type: type) -> bool:
        """Return whether this renderer has an own rule for given node type."""
        return cls.find_rule(node_type) is not None

    def processors(self, node: mknode.MkNode) -> list[processors.TextProcessor]:
        """Return the text processors to run on the Markdown of given node."""
        return node.get_processors()

    def finalize(self, output: BuildOutput, root: mk.MkNav) -> None:
        """Post-process a whole build (all pages rendered), in place. Default: nothing.

        Args:
            output: The build output
            root: The root nav of the build
        """

    async def render(self, node: mknode.MkNode) -> resources.NodeContent:
        """Render given node (unprocessed Markdown) and collect its resources."""
        if rule := self.find_rule(type(node)):
            # Rules only produce Markdown. Resources of nodes rendered by a rule
            # are flavour-specific and not collected yet.
            return resources.NodeContent(
                markdown=await rule(node, self), resources=resources.Resources()
            )
        return await node.get_content()

    async def render_markdown(self, node: mknode.MkNode) -> str:
        """Render the unprocessed Markdown of given node."""
        if rule := self.find_rule(type(node)):
            return await rule(node, self)
        return await node.to_md_unprocessed()

    def process(self, node: mknode.MkNode, text: str) -> str:
        """Run the text processors of given node on given text."""
        for proc in self.processors(node):
            text = proc.run(text)
        return text

    async def render_child(self, node: mknode.MkNode) -> resources.NodeContent:
        """Render a child node: content with the node's processors applied."""
        content = await self.render(node)
        content.markdown = self.process(node, content.markdown)
        return content

    async def render_children(
        self,
        nodes: list[mknode.MkNode],
        separator: str = "\n\n",
    ) -> str:
        """Render given nodes as children and join their Markdown."""
        return separator.join([(await self.render_child(node)).markdown for node in nodes])


def _get_template_rule(klass: type, renderers: list[type[Renderer]]) -> Rule | None:
    """Return a rule rendering the `[output.<key>]` template of the class's node file."""
    from mknodes.info import nodefile

    keys = [r.template_key for r in renderers if r.template_key]
    if not keys:
        return None
    try:
        file = nodefile.get_nodefile(klass)
    except (AssertionError, TypeError, OSError):  # classes without a source file
        return None
    if not file:
        return None
    template = next((file.output[k].template for k in keys if k in file.output), None)
    if template is None:
        return None

    async def render_template(node: mknode.MkNode, renderer: Renderer) -> str:
        return await node.env.render_string_async(template)

    return render_template


class MaterialRenderer(Renderer):
    """Material for MkDocs flavour (the default): nodes render themselves."""

    name = "material"


_current: contextvars.ContextVar[Renderer] = contextvars.ContextVar(
    "mknodes_renderer",
    default=MaterialRenderer(),  # noqa: B039
)


def current() -> Renderer:
    """Return the active renderer."""
    return _current.get()


@contextlib.contextmanager
def use(renderer: Renderer) -> Generator[Renderer]:
    """Make given renderer the active one inside the context."""
    token = _current.set(renderer)
    try:
        yield renderer
    finally:
        _current.reset(token)
