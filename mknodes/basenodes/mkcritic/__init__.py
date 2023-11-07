from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, get_args

from mknodes.basenodes import mkcontainer
from mknodes.utils import log, resources


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

    @property
    def marks(self):
        match self.typ:
            case "addition":
                return ("++", "++")
            case "deletion":
                return ("--", "--")
            case "highlight":
                return ("==", "==")
            case "comment":
                return (">>", "<<")
            case _:
                raise TypeError(self.typ)

    def _to_markdown(self) -> str:
        left, right = self.marks
        return f"{{{left}\n\n{super()._to_markdown()}\n\n{right}}}"

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        for typ in get_args(CriticMarkStr):
            node = MkCritic(f"This is type {typ}", typ=typ)
            page += mk.MkHeader(f"Type {typ!r}", level=3)
            page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    mkcritic = MkCritic("hello")
    print(mkcritic)
