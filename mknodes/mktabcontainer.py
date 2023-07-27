from __future__ import annotations

from collections.abc import Mapping
import logging
import textwrap

from mknodes import mkcontainer, mknode, mktabs, mktext
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkTabContainer(mkcontainer.MkContainer):
    items: list[mktabs.MkTab]

    def __init__(
        self,
        tabs: Mapping[str, str | mknode.MkNode] | list[mktabs.MkTab],
        *,
        header: str = "",
        select_tab: int | str | None = None,
        **kwargs,
    ):
        if isinstance(tabs, list):
            items = tabs
        else:
            items = [
                mktabs.MkTab(
                    k,
                    items=[mktext.MkText(v) if isinstance(v, str) else v],
                )
                for k, v in tabs.items()
            ]
        for tab in items:
            tab.parent_item = self
        match select_tab:
            case int():
                items[select_tab].select = True
            case str():
                pos = self._get_tab_pos(select_tab)
                items[pos].select = True
        super().__init__(items=items, header=header, **kwargs)

    def __getitem__(self, item: int | str):
        match item:
            case int():
                return self.items[item]
            case str():
                for tab in self.items:
                    if tab.title == item:
                        return tab
                raise IndexError(item)
            case _:
                raise TypeError(item)

    def __contains__(self, tab: str | mktabs.MkTab) -> bool:
        match tab:
            case mktabs.MkTab():
                return tab in self.items
            case str():
                return any(i.title == tab for i in self.items)
            case _:
                raise TypeError(tab)

    def _get_tab_pos(self, tab_title: str) -> int:
        item = next(i for i in self.items if i.title == tab_title)
        return self.items.index(item)

    def __setitem__(self, index: str, value: mktabs.MkTab | str):
        match value:
            case str():
                item = mktext.MkText(value)
                tab = mktabs.MkTab(index, items=[item])
            case mktabs.MkTab():
                tab = value
            case mknode.MkNode():
                tab = mktabs.MkTab(index, items=[value])
        if index in self:
            pos = self._get_tab_pos(index)
            self.items[pos] = tab
        else:
            self.items.append(tab)

    def __repr__(self):
        return helpers.get_repr(self, items=self.items)

    def to_dict(self):
        return {tab.title: str(tab) for tab in self.items}

    @staticmethod
    def examples():
        yield dict(tabs={"Tab 1": "Some markdown", "Tab 2": "Other Markdown"})


class MkTabbed(MkTabContainer):
    """pymdownx-based Tab block."""

    REQUIRED_EXTENSIONS = "pymdownx.tabbed"

    def _to_markdown(self) -> str:
        lines: list[str] = []
        for tab in self.items:
            indented_text = textwrap.indent(str(tab).rstrip("\n"), prefix="    ")
            selected = "+" if tab.select else ""
            lines.extend((f'==={selected} "{tab.title}"', indented_text))
        return "\n".join(lines) + "\n"


class MkTabBlock(MkTabContainer):
    """New blocks-based Tab block."""

    REQUIRED_EXTENSIONS = "pymdownx.blocks.tab"

    def _to_markdown(self) -> str:
        lines: list[str] = []
        for i, tab in enumerate(self.items):
            begin = f"/// tab | {tab.title}"
            if i == 0:
                begin += "\n    new: True"
            if tab.select:
                begin += "\n    select: True"
            content = str(tab).rstrip("\n")
            end = "///\n"
            lines.extend((begin, content, end))
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    tabs = dict(Tab1="Some text", Tab2="Another text")
    tabblock = MkTabbed(tabs)
    print(tabblock)
