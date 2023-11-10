from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from mknodes.basenodes import mkcontainer, mknode, mktabs, mktext
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


class MkTabContainer(mkcontainer.MkContainer):
    """Base class for nodes containing tabs."""

    items: list[mktabs.MkTab | mktabs.MkTabBlock]
    Tab: type[mktabs.MkTab | mktabs.MkTabBlock]
    ICON = "material/tab"

    def __init__(
        self,
        tabs: Mapping[str, str | mknode.MkNode | list] | list[mktabs.MkTab] | None = None,
        *,
        header: str = "",
        select_tab: int | str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            tabs: Tab data
            header: Section header
            select_tab: Tab which should be selected initially
            kwargs: Keyword arguments passed to parent
        """
        match tabs:
            case None:
                items = []
            case list():
                items = tabs
            case _:
                items = [self.Tab(title=k, content=v) for k, v in tabs.items()]
        self.select_tab = select_tab
        super().__init__(content=items, header=header, **kwargs)
        self.block_separator = "\n"

    def __getitem__(self, item: int | str) -> mktabs.MkTab | mktabs.MkTabBlock:
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

    def __contains__(self, tab: str | mktabs.MkTab | mktabs.MkTabBlock) -> bool:
        match tab:
            case mktabs.MkTab() | mktabs.MkTabBlock():
                return tab in self.items
            case str():
                return any(i.title == tab for i in self.items)
            case _:
                raise TypeError(tab)

    def add_tab(
        self,
        title: str,
        content: str | mknode.MkNode | list[str] | list[mknode.MkNode],
        *,
        select: bool = False,
    ) -> mktabs.MkTab | mktabs.MkTabBlock:
        """Append a tab to existing ones.

        Arguments:
            title: Title of the new tab
            content: content of the new tab
            select: Whether new tab should get selected initially
        """
        tab = self.Tab(title=title, content=content, select=select)
        self.append(tab)
        return tab

    def _get_tab_pos(self, tab_title: str) -> int:
        item = next(i for i in self.items if i.title == tab_title)
        return self.items.index(item)

    def set_selected(self, index: int | str):
        """Set tab with given index as selected.

        Arguments:
            index: Index or title of the tab which should be selected
        """
        self.select_tab = self._get_tab_pos(index) if isinstance(index, str) else index
        for i, item in enumerate(self.items):
            item.select = i == self.select_tab

    def __setitem__(self, index: str, value: mknode.MkNode | str):
        match value:
            case str():
                item = mktext.MkText(value)
                tab = self.Tab(title=index, content=item)
            case mktabs.MkTab() | mktabs.MkTabBlock():
                tab = value
            case mknode.MkNode():
                tab = self.Tab(title=index, content=value)
        if index in self:
            pos = self._get_tab_pos(index)
            self.items[pos] = tab
        else:
            self.items.append(tab)

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            tabs=self.items,
            select_tab=self.select_tab,
            _filter_empty=True,
        )

    def _to_markdown(self) -> str:
        if not self.items:
            return ""
        if self.select_tab is not None:
            self.set_selected(self.select_tab)
        self.items[0].new = True
        return self.block_separator.join(str(i) for i in self.items)


if __name__ == "__main__":
    tabs = dict(Tab1="Some text", Tab2="Another text")
    tabblock = MkTabContainer(tabs)
    print(tabblock)
