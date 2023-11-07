from __future__ import annotations

from typing import Any

from mknodes.basenodes import mkcontainer
from mknodes.data import tools
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


class MkDevTools(mkcontainer.MkContainer):
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
        super().__init__(**kwargs)
        self._tools = tools

    def __repr__(self):
        return reprhelpers.get_repr(self, tools=self._tools, _filter_empty=True)

    @property
    def tools(self) -> list[tools.Tool]:  # type: ignore[return]
        match self._tools:
            case list():
                return self._tools
            case None:
                return self.ctx.metadata.tools
            case _:
                raise TypeError(self._tools)

    @property
    def items(self):
        import mknodes as mk

        items = []
        for t in self.tools:
            cfg_node = mk.MkCode(t.cfg or "", language=t.config_syntax)
            code = mk.MkCode(f"pip install {t.identifier}", language="bash")
            link = mk.MkLink(t.url, "More information")
            in_adm = [f"To install {t.identifier}:", code, link]
            section = [
                mk.MkHeader(t.title),
                mk.MkText(t.description),
                mk.MkCode(t.setup_cmd, language="md") if t.setup_cmd else None,
                mk.MkAdmonition(cfg_node, collapsible=True, title="Config", typ="quote"),
                mk.MkAdmonition(in_adm, collapsible=True, title=f"Installing {t.title}"),
            ]
            items.extend(i for i in section if i is not None)
        for item in items:
            item.parent = self
        return items

    @items.setter
    def items(self, value):
        pass

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkDevTools()
        page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    setup_text = MkDevTools(build_backend="flit")
    print(setup_text)
