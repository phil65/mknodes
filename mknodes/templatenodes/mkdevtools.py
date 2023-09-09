from __future__ import annotations

from typing import Any

from mknodes.basenodes import mkadmonition, mkcode, mkcontainer, mkheader, mklink, mktext
from mknodes.data import tools
from mknodes.info import folderinfo
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


class MkDevTools(mkcontainer.MkContainer):
    """Node showing information about used dev tools."""

    ICON = "material/wrench"
    STATUS = "new"

    def __init__(
        self,
        tools: list[tools.ToolStr] | None = None,
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
                return [tools.TOOLS[i] for i in self._tools]
            case None:
                return self.ctx.metadata.tools
            case _:
                raise TypeError(self._tools)

    @property
    def items(self):
        items = []
        info = (
            self.associated_project.folderinfo
            if self.associated_project
            else folderinfo.FolderInfo()
        )
        for tool in self.tools:
            cfg = tool.get_config(info)
            code = mkcode.MkCode(cfg or "", language=tool.config_syntax)
            items.extend([mkheader.MkHeader(tool.title), mktext.MkText(tool.description)])
            if tool.setup_cmd:
                items.append(mkcode.MkCode(tool.setup_cmd, language="md"))
            items.extend(
                [
                    mkadmonition.MkAdmonition(
                        code,
                        collapsible=True,
                        title="Config",
                        typ="quote",
                    ),
                    mkadmonition.MkAdmonition(
                        [
                            f"To install {tool.identifier}:",
                            mkcode.MkCode(
                                f"pip install {tool.identifier}",
                                language="bash",
                            ),
                            mklink.MkLink(tool.url, "More information"),
                        ],
                        collapsible=True,
                        title=f"Installing {tool.title}",
                    ),
                ],
            )

        for item in items:
            item.parent = self
        return items

    @items.setter
    def items(self, value):
        pass

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkDevTools()
        page += mknodes.MkReprRawRendered(node, header="### From project")
        node = MkDevTools(["pre-commit"])
        page += mknodes.MkReprRawRendered(node, header="### Explicit")


if __name__ == "__main__":
    setup_text = MkDevTools(build_backend="flit")
    print(setup_text)
