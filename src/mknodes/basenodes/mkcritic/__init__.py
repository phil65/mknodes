from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

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
    ) -> None:
        """Constructor.

        Args:
            content: Content to mark
            typ: Mark type
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(content=content, **kwargs)
        self.typ = typ

    @property
    def marks(self) -> tuple[str, str]:
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

    async def get_content(self) -> resources.NodeContent:
        """Single-pass: get content with critic formatting and resources."""
        content = await super().get_content()
        left, right = self.marks
        md = f"{{{left}\n\n{content.markdown}\n\n{right}}}"
        return resources.NodeContent(markdown=md, resources=content.resources)

    async def to_md_unprocessed(self) -> str:
        content = await self.get_content()
        return content.markdown


if __name__ == "__main__":
    mkcritic = MkCritic("hello")
    print(mkcritic)
