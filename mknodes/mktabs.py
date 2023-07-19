from __future__ import annotations

from collections.abc import Mapping
import logging
import textwrap

from mknodes import mkcontainer, mknode, mktext, utils


logger = logging.getLogger(__name__)


class MkTab(mkcontainer.MkContainer):
    def __init__(
        self,
        title: str,
        items: list | None = None,
        *,
        select: bool = False,
        attrs: dict | None = None,
        **kwargs,
    ):
        super().__init__(items=items, **kwargs)
        self.title = title
        self.select = select
        self.attrs = attrs

    @staticmethod
    def examples():
        yield from ()


class MkBaseTabWidget(mkcontainer.MkContainer):
    def __init__(
        self,
        tabs: Mapping[str, str | mknode.MkNode] | list[MkTab],
        header: str = "",
        **kwargs,
    ):
        if isinstance(tabs, list):
            items = tabs
        else:
            items = [
                MkTab(
                    k,
                    items=[mktext.MkText(v) if isinstance(v, str) else v],
                )
                for k, v in tabs.items()
            ]
        for tab in items:
            tab.parent_item = self
        super().__init__(items=items, header=header)

    def __repr__(self):
        return utils.get_repr(self, items=self.items)

    def to_dict(self):
        return {tab.title: str(tab) for tab in self.items}

    @staticmethod
    def examples():
        yield dict(tabs={"Tab 1": "Some markdown", "Tab 2": "Other Markdown"})


class MkTabbed(MkBaseTabWidget):
    """pymdownx-based Tab block."""

    REQUIRED_EXTENSIONS = "pymdownx.tabbed"

    def _to_markdown(self) -> str:
        lines: list[str] = []
        for tab in self.items:
            indented_text = textwrap.indent(str(tab).rstrip("\n"), prefix="    ")
            lines.extend((f'=== "{tab.title}"', indented_text))
        return "\n".join(lines) + "\n"


class MkTabBlock(MkBaseTabWidget):
    """pymdownx-based Tab block."""

    REQUIRED_EXTENSIONS = "pymdownx.blocks.tab"

    def _to_markdown(self) -> str:
        lines: list[str] = []
        for tab in self.items:
            # TODO: perhaps always add "new: true" to first tab?
            lines.extend((f"/// tab | {tab.title}", str(tab).rstrip("\n"), "///\n"))
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    tabs = dict(Tab1="Some text", Tab2="Another text")
    tabblock = MkTabbed(tabs)
    print(tabblock)
