"""Render-once cache for nodes whose children / content come from a Jinja template."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mknodes import rendering


if TYPE_CHECKING:
    from mknodes.jinja.nodeenvironment import NodeEnvironment, RenderResult


class _State:
    __slots__ = ("results", "tree")

    def __init__(self) -> None:
        self.results: dict[type, RenderResult] = {}
        self.tree: RenderResult | None = None


class TemplateRenderMixin:
    """Renders the node's template once and serves both children and content from it.

    `{{ node }}` output depends on the active renderer (flavour), so results are cached
    per renderer class. The tree (`get_render_result()`, used for children) is the first
    result, so children stay the same objects whatever gets rendered afterwards.
    Setting any attribute of the node drops the cache (the template may use it).
    """

    env: NodeEnvironment

    def render_kwargs(self) -> dict[str, Any]:
        """Keyword arguments for `NodeEnvironment.render_nodes[_async]()`."""
        raise NotImplementedError

    def __setattr__(self, name: str, value: Any) -> None:
        if name != "_render_state":
            self.__dict__.pop("_render_state", None)
        super().__setattr__(name, value)

    def _get_state(self) -> _State:
        if (state := self.__dict__.get("_render_state")) is None:
            state = self.__dict__["_render_state"] = _State()
        return state

    def get_render_result(self) -> RenderResult:
        """Return the render the node's children come from (sync, renders if needed)."""
        state = self._get_state()
        if state.tree is None:
            renderer = type(rendering.current())
            if (result := state.results.get(renderer)) is None:
                result = self.env.render_nodes(**self.render_kwargs())
                state.results[renderer] = result
            state.tree = result
        return state.tree

    async def get_render_result_async(self) -> RenderResult:
        """Return the render for the active renderer (renders if needed)."""
        state = self._get_state()
        renderer = type(rendering.current())
        if (result := state.results.get(renderer)) is None:
            result = await self.env.render_nodes_async(**self.render_kwargs())
            state.results[renderer] = result
        if state.tree is None:
            state.tree = result
        return result
