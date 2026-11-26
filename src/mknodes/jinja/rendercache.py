"""Render-once cache for nodes whose children / content come from a Jinja template."""

from typing import TYPE_CHECKING, Any

from mknodes import rendering


if TYPE_CHECKING:
    from mknodes.jinja.nodeenvironment import NodeEnvironment, RenderResult


_epoch = 0


def invalidate_all() -> None:
    """Drop all cached template renders (e.g. after global state like link excludes changed)."""
    global _epoch
    _epoch += 1


def cache_key() -> tuple[type, bool]:
    """Key for renders: active renderer class and whether a Jinja pass follows."""
    return type(rendering.current()), rendering.in_jinja_pass()


class _State:
    __slots__ = ("epoch", "results", "tree")

    def __init__(self) -> None:
        self.epoch = _epoch
        self.results: dict[tuple[type, bool], RenderResult] = {}
        self.tree: RenderResult | None = None


class TemplateRenderMixin:
    """Renders the node's template once and serves both children and content from it.

    `{{ node }}` output depends on the active renderer (flavour) and on whether a Jinja
    pass follows (`rendering.literal()`), so results are cached per renderer class and
    pass. The tree (`get_render_result()`, used for children) is the first
    result, so children stay the same objects whatever gets rendered afterwards.
    Setting any attribute of the node drops the cache (the template may use it).
    """

    env: NodeEnvironment

    def render_kwargs(self) -> dict[str, Any]:
        """Keyword arguments for `NodeEnvironment.render_nodes()`."""
        raise NotImplementedError

    def __setattr__(self, name: str, value: Any) -> None:
        if name != "_render_state":
            self.__dict__.pop("_render_state", None)
        super().__setattr__(name, value)

    def _get_state(self) -> _State:
        state = self.__dict__.get("_render_state")
        if state is None or state.epoch != _epoch:
            state = self.__dict__["_render_state"] = _State()
        return state

    def get_render_result(self) -> RenderResult:
        """Return the render the node's children come from (sync, renders if needed)."""
        state = self._get_state()
        if state.tree is None:
            key = cache_key()
            if (result := state.results.get(key)) is None:
                result = self.env.render_nodes(**self.render_kwargs())
                state.results[key] = result
            state.tree = result
        return state.tree

    def current_render_result(self) -> RenderResult:
        """Return the render for the active renderer (renders if needed)."""
        state = self._get_state()
        key = cache_key()
        if (result := state.results.get(key)) is None:
            result = self.env.render_nodes(**self.render_kwargs())
            state.results[key] = result
        if state.tree is None:
            state.tree = result
        return result
