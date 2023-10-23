from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, get_args

from mknodes.basenodes import mkcontainer
from mknodes.utils import log, reprhelpers, resources


if TYPE_CHECKING:
    import mknodes as mk

logger = log.get_logger(__name__)

CriticMarkStr = Literal["addition", "deletion", "comment", "highlight"]


class MkCritic(mkcontainer.MkContainer):
    """MkCritic block."""

    ICON = "material/format-text"
    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.critic")]

    def __init__(
        self,
        content: str | mk.MkNode | list,
        *,
        typ: CriticMarkStr = "highlight",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            content: Content to mark
            typ: Mark type
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(content=content, **kwargs)
        self.typ = typ

    def __repr__(self):
        return reprhelpers.get_repr(self, content=self.items, typ=self.typ)

    def _to_markdown(self) -> str:
        match self.typ:
            case "addition":
                left, right = ("++", "++")
            case "deletion":
                left, right = ("--", "--")
            case "highlight":
                left, right = ("==", "==")
            case "comment":
                left, right = (">>", "<<")
            case _:
                raise TypeError(self.typ)
        return f"{{{left}\n\n{super()._to_markdown()}\n\n{right}}}"

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        page += "The MkCritic node can be used to display text diffs."
        for typ in get_args(CriticMarkStr):
            node = MkCritic(f"This is type {typ}", typ=typ)
            page += mk.MkHeader(f"Type {typ!r}", level=3)
            page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    mkcritic = MkCritic("hello")
    print(mkcritic)
