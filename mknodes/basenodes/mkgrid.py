from __future__ import annotations

from mknodes.basenodes import mkcontainer, mknode
from mknodes.utils import log, reprhelpers, xmlhelpers as xml


logger = log.get_logger(__name__)


class MkGridCard(mkcontainer.MkContainer):
    """Node representing a single grid card."""

    ICON = "material/square-medium"
    STATUS = "new"

    def __init__(
        self,
        content: list | str | mknode.MkNode | None = None,
        **kwargs,
    ):
        super().__init__(content=content, **kwargs)

    def _to_markdown(self) -> str:
        item_str = "\n".join(i.to_markdown() for i in self.items)
        lines = item_str.split("\n")
        result = [f"-   {lines[0]}"]
        result.extend(f"    {i}" for i in lines[1:])
        return "\n".join(result) + "\n"


class MkGrid(mkcontainer.MkContainer):
    """Node for showing a grid."""

    ICON = "material/view-grid"
    items: list[MkGridCard]

    def __init__(
        self,
        cards: list[str | mknode.MkNode] | None = None,
        *,
        header: str = "",
        **kwargs,
    ):
        match cards:
            case None:
                items = []
            case list():
                items = [
                    (card if isinstance(card, MkGridCard) else MkGridCard(card))
                    for card in cards
                ]
        super().__init__(content=items, header=header, **kwargs)

    def __repr__(self):
        cards = []
        for item in self.items:
            if len(item.items) == 1:
                cards.append(reprhelpers.to_str_if_textnode(item.items[0]))
            else:
                cards.append(item)
        return reprhelpers.get_repr(self, cards=cards)

    def get_element(self) -> xml.Div:
        root = xml.Div("grid cards", markdown=True)
        content = "".join(str(i) for i in self.items) if self.items else ""
        root.text = "\n\n" + content + "\n"
        return root

    def _to_markdown(self) -> str:
        root = self.get_element()
        return root.to_string(space="")

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        # only works for Mkdocs-material sponsors.
        ls = ["Item 1", "Item 2", "Item 3"]
        item_1 = mk.MkList(ls)
        item_2 = mk.MkKeys(keys=["Ctrl+A"])
        grid = MkGrid(cards=[item_1, item_2])
        page += mk.MkReprRawRendered(grid)


if __name__ == "__main__":
    import mknodes

    keys = mknodes.MkKeys(keys="Ctrl+A")
    grid = MkGrid(cards=[keys, keys])
    print(grid)
