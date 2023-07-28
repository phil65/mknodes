from __future__ import annotations

import logging
import textwrap

from mknodes import mkblock, mkcontainer, mknode, mktext


logger = logging.getLogger(__name__)


class MkBlockTab(mkblock.MkBlock):
    def __init__(
        self,
        title: str,
        content: str | mknode.MkNode,
        *,
        new: bool | None = None,
        select: bool | None = None,
    ):
        super().__init__(
            "tab",
            content=str(content),
            argument=title,
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
    def __init__(
        self,
        title: str,
        content: list | str | mknode.MkNode | None = None,
        *,
        select: bool = False,
        attrs: dict | None = None,
        **kwargs,
    ):
        match content:
            case None:
                items: list[mknode.MkNode] = []
            case str():
                items = [mktext.MkText(content)]
            case mknode.MkNode():
                items = [content]
            case list():
                items = content
            case _:
                raise TypeError(content)
        super().__init__(items=items, **kwargs)
        self.title = title
        self.select = select
        self.attrs = attrs

    @staticmethod
    def create_example_page(page):
        import mknodes

        # We can add single tabs to a page by themselves.
        # It is recommended to use a Tab container though.
        tab_1 = MkTab("A Title", content="test")
        tab_2 = MkTab("Another Title", content=mknodes.MkAdmonition("Yeah"))
        page += tab_1
        page += tab_2
        code = str(tab_1) + "\n" + str(tab_2)
        page += mknodes.MkCode(code, header="Markdown", language="markdown")

    def _to_markdown(self) -> str:
        item_str = "\n\n".join(i.to_markdown() for i in self.items)
        indented_text = textwrap.indent(item_str.rstrip("\n"), prefix="    ")
        selected = "+" if self.select else ""
        lines = [f'==={selected} "{self.title}"', indented_text]
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    tab = MkBlockTab(content="test", title="test", new=True)
    print(tab)
