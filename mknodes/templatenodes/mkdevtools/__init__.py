from __future__ import annotations

from typing import Any

from mknodes.templatenodes import mktemplate
from mknodes.data import tools
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkDevTools(mktemplate.MkTemplate):
    """Node showing information about used dev tools."""

    ICON = "material/wrench"
    STATUS = "new"
    VIRTUAL_CHILDREN = True

    def __init__(
        self,
        tools: list[tools.Tool] | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            tools: Tools to show install / setup instructions for.
                            If None, tools will be pulled from project.
            kwargs: Keyword arguments passed to parent
        """
        super().__init__("output/markdown/template", **kwargs)
        self._tools = tools

    @property
    def tools(self) -> list[tools.Tool]:
        match self._tools:
            case list():
                return self._tools
            case None:
                return self.ctx.metadata.tools
            case _:
                raise TypeError(self._tools)

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkDevTools()
        page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    setup_text = MkDevTools.with_context()
    print(setup_text)
