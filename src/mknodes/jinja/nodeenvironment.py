import annotationlib
import contextvars
import dataclasses
import functools
import inspect
import os
import pathlib
from typing import TYPE_CHECKING, Any
import warnings

import jinja2
from jinja2 import compiler
import jinjarope
from jinjarope import inspectfilters

from mknodes import inputs, rendering
from mknodes.utils import buildtime, diagnostics, log, pathhelpers


if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from jinja2.runtime import Context

    import mknodes as mk
    from mknodes.utils.resources import Resources


logger = log.get_logger(__name__)


@dataclasses.dataclass(eq=False)
class _Collector:
    """Nodes created during one render call of `env`."""

    env: NodeEnvironment
    parent: _Collector | None
    nodes: list[mk.MkNode] = dataclasses.field(default_factory=list)
    resources: dict[int, Resources] = dataclasses.field(default_factory=dict)


_collector: contextvars.ContextVar[_Collector | None] = contextvars.ContextVar(
    "mknodes_render_collector", default=None
)


@dataclasses.dataclass(eq=False)
class RenderResult:
    """Result of a single template render: Markdown plus the nodes it created."""

    markdown: str
    """The rendered text."""
    nodes: list[mk.MkNode]
    """All nodes created by node filters / globals of the environment, in creation order."""
    owner: mk.MkNode
    """The node of the environment (parent of the top-level created nodes)."""
    resources: dict[int, Resources] = dataclasses.field(default_factory=dict)
    """Resources of the nodes written with `{{ node }}` (by `id(node)`)."""

    @functools.cached_property
    def children(self) -> list[mk.MkNode]:
        """Created nodes which are direct children of the environment's node (cached)."""
        return [i for i in self.nodes if i.parent is self.owner]

    def get_resources(self, node: mk.MkNode) -> Resources:
        """Resources of given created node (rendered only if it was not written out)."""
        if (res := self.resources.get(id(node))) is not None:
            return res
        return (node.get_content()).resources


class NodeCodeGenerator(compiler.CodeGenerator):
    """Code generator rendering nodes written with `{{ node }}` via the environment.

    `{{ x }}` normally compiles to `str(x)`. For nodes this generates
    `str(x if not isinstance(x, MkNode) else environment._render_output(x))`, which
    renders the node in the active flavour and remembers its resources for the render.
    """

    def _output_child_pre(self, node: Any, frame: Any, finalize: Any) -> None:
        super()._output_child_pre(node, frame, finalize)
        self.write("(_mk_v if not isinstance((_mk_v := ")

    def _output_child_post(self, node: Any, frame: Any, finalize: Any) -> None:
        self.write("), environment.node_type) else environment._render_output(_mk_v))")
        super()._output_child_post(node, frame, finalize)


# Deprecated async node methods -> their sync versions, for templates calling them.
_SYNC_METHODS = {
    "to_markdown": "to_markdown_sync",
    "to_html": "to_html_sync",
    "get_resources": "get_resources_sync",
    "get_toc": "get_toc_sync",
}


class NodeContext(jinjarope.environment.Context):
    """Template context: `node.to_markdown()` etc. call the sync versions.

    Templates are sync; the async methods of `MkNode` (deprecated) would return
    coroutines. Removed in mknodes 5.0 together with the async methods.
    """

    def call(self, obj: Any, /, *args: Any, **kwargs: Any) -> Any:
        name = getattr(obj, "__name__", None)
        owner = getattr(obj, "__self__", None)
        if name in _SYNC_METHODS and isinstance(owner, self.environment.node_type):  # type: ignore[attr-defined]
            obj = getattr(owner, _SYNC_METHODS[name])
        return super().call(obj, *args, **kwargs)


class NodeEnvironment(jinjarope.Environment):
    """Jinja Node environment.

    A Jinja Environment specifically for MkNode instances.

    - Sets the parent for the filters
    - Puts node context in jinja namespace
    - collects the nodes created by a render (per render call, see `render_nodes`)
    - renders nodes written with `{{ node }}` in the active flavour (sync: templates
      only read resolved inputs, see `mknodes.inputs`)
    """

    code_generator_class = NodeCodeGenerator

    def __init__(self, node: mk.MkNode, **kwargs: Any) -> None:
        """Constructor.

        Args:
            node: Node this environment belongs to.
            kwargs: Optional keyword arguments passed to parent
        """
        import mknodes as mk

        super().__init__(**kwargs)
        self.context_class = NodeContext
        self.node = node
        self.node_type = mk.MkNode
        # Deprecated: nodes of the last render (use `render_nodes()`).
        self.rendered_nodes: list[mk.MkNode] = list()
        self.rendered_children: list[mk.MkNode] = list()

        self._node_filters: dict[str, Callable[..., mk.MkNode]] = {}
        # Wrapper classes for `mk.MkXyz(...)` in templates, created on first access
        # (creating ~85 classes per environment is expensive and rarely needed).
        self._wrapped_klasses = _WrappedClasses(self)

        for kls_name in mk.__all__:

            def wrapped(
                ctx: Context,
                *args: Any,
                kls_name: str = kls_name,
                **kwargs: Any,
            ) -> mk.MkNode:
                kls = getattr(mk, kls_name)
                try:
                    node = kls(*args, parent=self.node, **kwargs)
                    self._record(node)
                except Exception as e:  # noqa: BLE001
                    # Create error message with signature
                    # only names / defaults needed: FORWARDREF never fails on annotations
                    sig = inspect.signature(
                        kls.__init__, annotation_format=annotationlib.Format.FORWARDREF
                    )
                    params = []
                    for param_name, param in sig.parameters.items():
                        if param_name in ("self", "parent"):
                            continue
                        if param.kind == inspect.Parameter.VAR_KEYWORD:
                            params.append(f"**{param_name}")
                        elif param.kind == inspect.Parameter.VAR_POSITIONAL:
                            params.append(f"*{param_name}")
                        elif param.default is inspect.Parameter.empty:
                            params.append(f"{param_name}")
                        else:
                            params.append(f"{param_name}={param.default!r}")
                    signature_str = f"{kls_name}({', '.join(params)})"

                    error_msg = (
                        f"Failed to create {kls_name} node in Jinja template.\n"
                        f"Error: {type(e).__name__}: {e}\n"
                        f"Signature: {signature_str}\n"
                        f"Called with args={args!r}, kwargs={kwargs!r}"
                    )
                    template = getattr(ctx, "name", None)
                    diagnostics.report(
                        "node",
                        f"Failed to create {kls_name}: {diagnostics.describe_exception(e)}",
                        page=diagnostics.current_page.get() or diagnostics.node_page(self.node),
                        location=f"template {template}" if template else None,
                    )

                    # Create MkText node with error message
                    error_node = mk.MkText(error_msg, parent=self.node)
                    self._record(error_node)
                    return error_node
                else:
                    return node

            self._node_filters[kls_name] = jinja2.pass_context(wrapped)
        self.setup_environment()

    def setup_environment(self) -> None:
        """Set up the environment by adding node/context specific filters / globals.

        Mainly this adds wrapper functions / classes for all the MkNodes in order
        to auto-set the node parent (and that way the context) and to collect
        the rendered nodes.
        """
        nodefile = self.node.get_nodefile()
        ctx_loader = self.node.ctx.env_config.loader
        # Keep the loader while its inputs stay the same: Jinja caches compiled
        # templates per loader, a new loader per render means compiling every time.
        loader_key = (ctx_loader, type(self.node))
        if getattr(self, "_loader_key", None) != loader_key:
            path = inspectfilters.get_file(self.node.__class__)  # type: ignore[arg-type]
            class_path = pathlib.Path(path or "").parent.as_posix()
            loaders = [
                ctx_loader or jinjarope.FileSystemLoader("docs/"),
                jinjarope.FileSystemLoader(class_path),
                jinjarope.FsSpecProtocolPathLoader(),
            ]
            if nodefile:
                loader = jinjarope.NestedDictLoader(nodefile._data)
                loaders.insert(0, loader)
            self.loader = jinjarope.ChoiceLoader(loaders)
            self._loader_key = loader_key

        self.filters.update(self._node_filters)
        self.filters.update(_INPUT_FILTERS)
        self.filters["string"] = self._string_filter
        self.filters["get_doc"] = _get_doc
        self.globals.update(_INPUT_GLOBALS)  # pyright: ignore[reportArgumentType]
        self.globals["parent_page"] = self.node.parent_page  # pyright: ignore[reportArgumentType]
        self.globals["parent_nav"] = i[-1] if (i := self.node.parent_navs) else None  # pyright: ignore[reportArgumentType]
        self.globals["node"] = self.node  # pyright: ignore[reportArgumentType]
        self.globals["file"] = nodefile  # pyright: ignore[reportArgumentType]
        self.globals["mk"] = self._wrapped_klasses  # pyright: ignore[reportArgumentType]
        self.globals |= self.node.ctx.as_dict()

    # def get_extra_paths(self) -> list[str]:
    #     paths = [self.class_path]
    #     if self.node.parent_navs:
    #         nav = self.node.parent_navs[-1]
    #         if "created" in nav.metadata:
    #             file = nav.metadata["created"]["source_filename"]
    #             path = pathlib.Path(file).parent
    #             paths.append(path.as_posix())
    #     return paths

    def _record(self, node: mk.MkNode) -> None:
        """Add a node created by a filter / global of this env to the active render."""
        collector = _collector.get()
        while collector is not None and collector.env is not self:
            collector = collector.parent
        if collector is not None:
            collector.nodes.append(node)

    def _render_output(self, node: mk.MkNode) -> str:
        """Render a node written by `{{ node }}` (called by the generated template code).

        Same result as `str(node)`. The resources get remembered, so template nodes
        don't need to render their children again for them.
        """
        renderer = rendering.current()
        content = renderer.render(node)
        if not renderer.supports(type(node)) and (collector := _collector.get()) is not None:
            collector.resources[id(node)] = content.resources
        return renderer.process(node, content.markdown)

    def _string_filter(self, value: Any) -> str:
        """`string` filter: nodes get rendered like `{{ node }}`."""
        if isinstance(value, self.node_type):
            return self._render_output(value)
        return jinja2.filters.soft_str(value)

    def render_nodes(
        self,
        template_name: str | None = None,
        *,
        string: str | None = None,
        variables: dict[str, Any] | None = None,
        block_name: str | None = None,
        parent_template: str | None = None,
    ) -> RenderResult:
        """Render a template (or a template string) once: Markdown + created nodes.

        Nodes are collected per render call (context variable), so concurrent renders
        and nested renders of other environments don't see each other's nodes. Nodes of
        nested renders of this environment (e.g. the `render_string` filter) also count
        for the outer render.

        Args:
            template_name: Template to render
            string: Template string to render (instead of a template name)
            variables: Extra variables for this render call
            block_name: Render specific block from the template
            parent_template: The name of the parent template importing this template
        """
        self.setup_environment()
        parent = _collector.get()
        collector = _Collector(self, parent)
        token = _collector.set(collector)
        try:
            if string is not None:
                markdown = super().render_string(string, variables)
            else:
                assert template_name is not None
                markdown = super().render_template(
                    template_name,
                    variables=variables,
                    block_name=block_name,
                    parent_template=parent_template,
                )
        finally:
            _collector.reset(token)
        if parent is not None and parent.env is self:
            parent.nodes.extend(collector.nodes)
            parent.resources |= collector.resources
        result = RenderResult(markdown, collector.nodes, self.node, collector.resources)
        # Deprecated: nodes of the last render, kept for backwards compatibility.
        self.rendered_nodes = result.nodes
        self.rendered_children = result.children
        return result

    async def render_nodes_async(
        self,
        template_name: str | None = None,
        *,
        string: str | None = None,
        variables: dict[str, Any] | None = None,
        block_name: str | None = None,
        parent_template: str | None = None,
    ) -> RenderResult:
        """Deprecated (removed in 5.0): rendering is sync, use `render_nodes()`."""
        _deprecated("NodeEnvironment.render_nodes_async()", "render_nodes()")
        return self.render_nodes(
            template_name,
            string=string,
            variables=variables,
            block_name=block_name,
            parent_template=parent_template,
        )

    def render_template(
        self,
        template_name: str,
        variables: dict[str, Any] | None = None,
        block_name: str | None = None,
        parent_template: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Render a loaded template.

        Args:
            template_name: Template name
            variables: Extra variables for this render call
            block_name: Render specific block from the template
            parent_template: The name of the parent template importing this template
            kwargs: Additional variables for the render call
        """
        result = self.render_nodes(
            template_name,
            variables=(variables or {}) | kwargs,
            block_name=block_name,
            parent_template=parent_template,
        )
        return result.markdown

    async def render_template_async(
        self,
        template_name: str,
        variables: dict[str, Any] | None = None,
        block_name: str | None = None,
        parent_template: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Deprecated (removed in 5.0): rendering is sync, use `render_template()`."""
        _deprecated("NodeEnvironment.render_template_async()", "render_template()")
        return self.render_template(
            template_name,
            variables,
            block_name=block_name,
            parent_template=parent_template,
            **kwargs,
        )

    def render_string(
        self,
        string: str,
        variables: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> str:
        """Render a template string.

        Args:
            string: String to render
            variables: Extra variables for the environment
            kwargs: Additional variables for the render call
        """
        return self.render_nodes(string=string, variables=(variables or {}) | kwargs).markdown

    async def render_string_async(
        self,
        string: str,
        variables: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> str:
        """Deprecated (removed in 5.0): rendering is sync, use `render_string()`."""
        _deprecated("NodeEnvironment.render_string_async()", "render_string()")
        return self.render_string(string, variables, **kwargs)


def _deprecated(name: str, replacement: str) -> None:
    msg = f"{name} is deprecated (rendering is sync), use {replacement}. Removed in mknodes 5.0."
    warnings.warn(msg, DeprecationWarning, stacklevel=3)


class _WrappedClasses(dict[str, type]):
    """`mk` namespace of templates: node classes whose instances get attached to the node."""

    def __init__(self, env: NodeEnvironment) -> None:
        super().__init__()
        self.env = env

    def __missing__(self, kls_name: str) -> type:
        import mknodes as mk

        if kls_name not in mk.__all__:
            raise KeyError(kls_name)
        klass: Any = getattr(mk, kls_name)
        env = self.env

        class _WrappedMkNode(klass):
            def __post_init__(_self) -> None:  # noqa: N805
                _self.parent = env.node
                env._record(_self)

        functools.update_wrapper(_WrappedMkNode, klass, updated=[])
        # we add <locals> here so that the classes get filtered in iter_subclasses
        _WrappedMkNode.__qualname__ = "<locals>." + _WrappedMkNode.__qualname__
        self[kls_name] = _WrappedMkNode
        return _WrappedMkNode


def _load_file(path: str | os.PathLike[str]) -> str:
    """`load_file` filter: remote files come from the inputs store (lock file)."""
    return pathhelpers.load_file(path)


def _check_output(
    call: str | Sequence[str],
    cwd: str | os.PathLike[str] | None = None,
    use_cache: bool = False,
) -> str | None:
    """`check_output` filter: the command runs in the resolve phase (inputs kind `command`)."""
    if not call:
        return None
    command = call if isinstance(call, str) else " ".join(call)
    return inputs.get_input("command", call=command, cwd=os.fspath(cwd) if cwd else None)


# jinjarope filters / globals doing I/O or reading the clock, replaced by versions
# reading resolved inputs (rendering stays free of I/O) / the fixed build time.
_INPUT_FILTERS: dict[str, Callable[..., Any]] = {
    "load_file": _load_file,
    "check_output": _check_output,
}
_INPUT_GLOBALS: dict[str, Callable[..., Any]] = {
    "now": buildtime.now,
    "utcnow": buildtime.utcnow,
}


def _get_doc(obj: Any, **kwargs: Any) -> str:
    """`get_doc` filter: docstrings are data, the page's Jinja pass must not render them."""
    return rendering.literal(inspectfilters.get_doc(obj, **kwargs))


if __name__ == "__main__":
    import mknodes as mk

    node = mk.MkText.with_context()
    env = NodeEnvironment(node)
    # txt = "{{ metadata.required_python_version | MkAdmonition | apply_mod('ParallaxEffect') }}"
    # print(env.render_string(txt))
    # print(env.rendered_nodes)
    # text = env.render_string(r"{{ 'test' | MkHeader }}")
    result = env.render_nodes(string=r"{{ 50 | MkProgressBar }}")
    print(result.markdown, result.nodes)
    # env.render_string(r"{{test('hallo')}}")
