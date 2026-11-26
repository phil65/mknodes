"""Node environment for the minijinja backend (needs the `minijinja` extra)."""

from typing import TYPE_CHECKING, Any

from jinjarope.minijinjaenv import MiniJinjaEnvironment

from mknodes.jinja.nodeenvironment import NodeEnvironmentBase


if TYPE_CHECKING:
    import mknodes as mk


class MiniJinjaNodeEnvironment(NodeEnvironmentBase, MiniJinjaEnvironment):
    """Node environment rendering with minijinja (`jinja_engine = "minijinja"`)."""

    def __init__(self, node: mk.MkNode, **kwargs: Any) -> None:
        """Constructor.

        Args:
            node: Node this environment belongs to.
            kwargs: Optional keyword arguments passed to `MiniJinjaEnvironment`
        """
        # `{{ node }}` renders via the finalizer (Jinja2: NodeCodeGenerator)
        MiniJinjaEnvironment.__init__(self, finalize=self._finalize_output, **kwargs)
        self._init_node(node)

    def _finalize_output(self, value: Any) -> Any:
        if isinstance(value, self.node_type):
            return self._render_output(value)
        return value
