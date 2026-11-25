from __future__ import annotations

import functools
import inspect
import pathlib
from typing import TYPE_CHECKING, Any

import jinja2
import jinjarope
from jinjarope import inspectfilters

from mknodes.utils import coroutines, log


if TYPE_CHECKING:
    from collections.abc import Callable

    from jinja2.runtime import Context

    import mknodes as mk


logger = log.get_logger(__name__)


class NodeEnvironment(jinjarope.Environment):
    """Jinja Node environment.

    A Jinja Environment specifically for MkNode instances.

    - Sets the parent for the filters
    - Puts node context in jinja namespace
    - collects rendered nodes
    """

    def __init__(self, node: mk.MkNode, **kwargs: Any) -> None:
        """Constructor.

        Args:
            node: Node this environment belongs to.
            kwargs: Optional keyword arguments passed to parent
        """
        super().__init__(enable_async=True, **kwargs)
        self.node = node
        self.rendered_nodes: list[mk.MkNode] = list()
        self.rendered_children: list[mk.MkNode] = list()

        import mknodes as mk

        self._node_filters: dict[str, Callable[..., mk.MkNode]] = {}
        # Wrapper classes for `mk.MkXyz(...)` in templates, created on first access
        # (creating ~85 classes per environment is expensive and rarely needed).
        self._wrapped_klasses = _WrappedClasses(self)

        for kls_name in mk.__all__:

            def wrapped(
                ctx: Context,  # pyright: ignore[reportUnusedParameter]
                *args: Any,
                kls_name: str = kls_name,
                **kwargs: Any,
            ) -> mk.MkNode:
                kls = getattr(mk, kls_name)
                try:
                    node = kls(*args, parent=self.node, **kwargs)
                    self.rendered_nodes.append(node)
                except Exception as e:  # noqa: BLE001
                    # Create error message with signature
                    sig = inspect.signature(kls.__init__)
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
                    logger.error(error_msg)  # noqa: TRY400

                    # Create MkText node with error message
                    error_node = mk.MkText(error_msg, parent=self.node)
                    self.rendered_nodes.append(error_node)
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
        path = inspectfilters.get_file(self.node.__class__)  # type: ignore[arg-type]
        class_path = pathlib.Path(path or "").parent.as_posix()

        loaders = [
            self.node.ctx.env_config.loader or jinjarope.FileSystemLoader("docs/"),
            jinjarope.FileSystemLoader(class_path),
            jinjarope.FsSpecProtocolPathLoader(),
        ]
        nodefile = self.node.get_nodefile()
        if nodefile:
            loader = jinjarope.NestedDictLoader(nodefile._data)
            loaders.insert(0, loader)
        self.loader = jinjarope.ChoiceLoader(loaders)

        self.filters.update(self._node_filters)
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

    def render_template(
        self,
        template_name: str,
        variables: dict[str, Any] | None = None,
        block_name: str | None = None,
        parent_template: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Render a loaded template (sync version).

        Rendered nodes can be collected from `rendered_nodes` attribute after this call.

        Args:
            template_name: Template name
            variables: Extra variables for this render call
            block_name: Render specific block from the template
            parent_template: The name of the parent template importing this template
            kwargs: Additional variables for the render call
        """
        # The environment is async: render via the async version (no global patching).
        coro = self.render_template_async(
            template_name,
            variables=variables,
            block_name=block_name,
            parent_template=parent_template,
            **kwargs,
        )
        return coroutines.run_sync(coro)

    async def render_template_async(
        self,
        template_name: str,
        variables: dict[str, Any] | None = None,
        block_name: str | None = None,
        parent_template: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Render a loaded template (async version).

        Rendered nodes can be collected from `rendered_nodes` attribute after this call.

        Args:
            template_name: Template name
            variables: Extra variables for this render call
            block_name: Render specific block from the template
            parent_template: The name of the parent template importing this template
            kwargs: Additional variables for the render call
        """
        self.rendered_nodes = []
        self.setup_environment()
        result = await super().render_template_async(
            template_name,
            variables=variables,
            block_name=block_name,
            parent_template=parent_template,
            **kwargs,
        )
        self.rendered_children = [i for i in self.rendered_nodes if i.parent == self.node]
        return result

    def render_string(
        self,
        string: str,
        variables: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> str:
        """Render a template string (sync version).

        Rendered nodes can be collected from `rendered_nodes` attribute after this call.

        Args:
            string: String to render
            variables: Extra variables for the environment
            kwargs: Additional variables for the render call
        """
        return coroutines.run_sync(self.render_string_async(string, variables, **kwargs))

    async def render_string_async(
        self,
        string: str,
        variables: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> str:
        """Render a template string (async version).

        Rendered nodes can be collected from `rendered_nodes` attribute after this call.

        Args:
            string: String to render
            variables: Extra variables for the environment
            kwargs: Additional variables for the render call
        """
        self.rendered_nodes = []
        self.setup_environment()
        result = await super().render_string_async(string, variables, **kwargs)
        self.rendered_children = [i for i in self.rendered_nodes if i.parent == self.node]
        return result


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
                env.rendered_nodes.append(_self)

        functools.update_wrapper(_WrappedMkNode, klass, updated=[])
        # we add <locals> here so that the classes get filtered in iter_subclasses
        _WrappedMkNode.__qualname__ = "<locals>." + _WrappedMkNode.__qualname__
        self[kls_name] = _WrappedMkNode
        return _WrappedMkNode


if __name__ == "__main__":
    import mknodes as mk

    node = mk.MkText.with_context()
    env = NodeEnvironment(node)
    # txt = "{{ metadata.required_python_version | MkAdmonition | apply_mod('ParallaxEffect') }}"
    # print(env.render_string(txt))
    # print(env.rendered_nodes)
    # text = env.render_string(r"{{ 'test' | MkHeader }}")
    text = env.render_string(r"{{ 50 | MkProgressBar }}")
    print(env.rendered_nodes)
    # env.render_string(r"{{test('hallo')}}")
