from __future__ import annotations

from typing import TYPE_CHECKING, Any, get_args

from mknodes.basenodes import mkblock
from mknodes.data import datatypes
from mknodes.utils import log, reprhelpers, resources


if TYPE_CHECKING:
    import mknodes as mk


logger = log.get_logger(__name__)


class MkDetailsBlock(mkblock.MkBlock):
    """Pymdownx-based details box."""

    ICON = "octicons/info-16"
    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.blocks.details")]
    STATUS = "new"

    def __init__(
        self,
        content: str | list | mk.MkNode | None = None,
        *,
        typ: datatypes.AdmonitionTypeStr = "info",
        expanded: bool | None = None,
        title: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            content: Admonition content
            typ: Admonition type
            expanded: Whether the details block should be expanded initially
            title: Optional Admonition title
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(
            "details",
            content=content or [],
            argument=title or "",
            attributes=dict(type=typ, open=expanded),
            **kwargs,
        )

    def __repr__(self):
        if len(self.items) == 1:
            content = reprhelpers.to_str_if_textnode(self.items[0])
        else:
            content = [reprhelpers.to_str_if_textnode(i) for i in self.items]
        return reprhelpers.get_repr(
            self,
            content=content,
            typ=self.typ,
            title=self.title,
            expanded=self.expanded,
            _filter_empty=True,
        )

    @property
    def title(self) -> str:
        return self.argument

    @title.setter
    def title(self, value: str):
        self.argument = value

    @property
    def typ(self) -> datatypes.AdmonitionTypeStr:
        return self.attributes["type"]

    @typ.setter
    def typ(self, value: datatypes.AdmonitionTypeStr):
        self.attributes["type"] = value

    @property
    def expanded(self) -> bool:
        return self.attributes["open"]

    @expanded.setter
    def expanded(self, value: bool):
        self.attributes["open"] = value

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        page += "MkDetailsBlock is a markdown extension based on pymdownx block syntax."
        url = "https://facelessuser.github.io/pymdown-extensions/extensions/blocks/api/"
        page += mk.MkLink(url, "More info", as_button=True)
        # AdmonitionTypeStr is a Literal containing all Admonition types
        for typ in get_args(datatypes.AdmonitionTypeStr):
            page += mk.MkHeader(f"Type '{typ}'", level=3)
            title = f"Details block with type {typ!r}"
            content = f"This is type **{typ}**"
            node = mk.MkDetailsBlock(typ=typ, content=content, title=title)
            page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    tab = MkDetailsBlock(content="test", title="test")
    print(tab)
