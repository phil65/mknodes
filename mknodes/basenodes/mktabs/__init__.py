from __future__ import annotations

import textwrap

from typing import Any

from mknodes.basenodes import mkblock, mkcontainer, mknode
from mknodes.utils import log, reprhelpers, resources


logger = log.get_logger(__name__)


class MkTabBlock(mkblock.MkBlock):
    """Node representing a single tab (new block style)."""

    ICON = "material/tab"
    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.blocks.tab")]

    def __init__(
        self,
        content: str | mknode.MkNode | list | None = None,
        title: str = "",
        *,
        new: bool | None = None,
        select: bool | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            title: Tab title
            content: Tab content
            new: Whether tab should start a new tab bloock
            select: Whether tab should be initially selected
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(
            "tab",
            content=content or [],
            argument=title,
            **kwargs,
        )
        if new is not None:
            self.new = new
        if select is not None:
            self.select = select

    @property
    def title(self):
        return self.argument

    @title.setter
    def title(self, value):
        self.argument = value

    @property
    def new(self):
        return self.attributes.get("new", False)

    @new.setter
    def new(self, value: bool):
        self.attributes["new"] = value

    @property
    def select(self):
        return self.attributes.get("select", False)

    @select.setter
    def select(self, value: bool):
        self.attributes["select"] = value


class MkTab(mkcontainer.MkContainer):
    """Node representing a single tab."""

    ICON = "material/tab"
    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.tabbed")]
    ATTR_LIST_SEPARATOR = "    "

    def __init__(
        self,
        content: list | str | mknode.MkNode | None = None,
        title: str = "",
        *,
        new: bool = False,
        select: bool = False,
        attrs: dict | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            title: Tab title
            content: Tab content
            new: Whether tab should start a new tab bloock
            select: Whether tab should be initially selected
            attrs: Additional attributes for the tab
            kwargs: Keyword arguments passed to parent
        """
        self.title = title
        self.select = select
        self.new = new
        self.attrs = attrs
        super().__init__(content=content, **kwargs)

    def __repr__(self):
        if len(self.items) == 1:
            content = reprhelpers.to_str_if_textnode(self.items[0])
        else:
            content = [reprhelpers.to_str_if_textnode(i) for i in self.items]
        return reprhelpers.get_repr(
            self,
            title=self.title,
            content=content,
            select=self.select,
            new=self.new,
            attrs=self.attrs,
            _filter_empty=True,
            _filter_false=True,
        )

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        # We can add single tabs to a page by themselves.
        # It is recommended to use a Tab container though.
        tab = MkTab("Tab content(1)", title="A Title")
        tab.annotations[1] = "Tabs can carry annotations."
        page += mk.MkReprRawRendered(tab, header="### With annotations")

    def attach_annotations(self, text: str) -> str:
        # we deal with attaching annotations ourselves.
        return text

    def _to_markdown(self) -> str:
        text = "\n\n".join(i.to_markdown() for i in self.items)
        text = text.rstrip("\n")
        if self.annotations:
            annotates = str(self.annotations)
            text = f"{text}\n{{ .annotate }}\n\n{annotates}"
        text = textwrap.indent(text, prefix="    ")
        if self.new:
            mark = "!"
        elif self.select:
            mark = "+"
        else:
            mark = ""
        lines = [f'==={mark} "{self.title}"', text]
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    tab = MkTabBlock(content="test", title="test", new=True)
    print(tab)
