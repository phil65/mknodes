from __future__ import annotations

from typing import Any, Literal, TYPE_CHECKING

from mknodes.basenodes import mkcontainer
from mknodes.utils import log, resources, xmlhelpers as xml

if TYPE_CHECKING:
    from mknodes.basenodes import mknode


logger = log.get_logger(__name__)


class MkSpeechBubble(mkcontainer.MkContainer):
    """Node for showing a css-based speech bubble."""

    ICON = "material/chat"
    CSS = [resources.CSSFile("speechbubble.css")]

    def __init__(
        self,
        content: str | mknode.MkNode | list | None = None,
        *,
        arrow: Literal["top", "bottom", "left", "right"] | None = "bottom",
        **kwargs: Any,
    ) -> None:
        self.arrow = arrow
        super().__init__(content=content or [], **kwargs)

    async def get_element(self) -> xml.Div:
        klass = f"speech {self.arrow}" if self.arrow else "speech"
        root = xml.Div(klass, markdown=True)
        root.text = "\n" + await super().to_md_unprocessed() + "\n"
        return root

    async def to_md_unprocessed(self) -> str:
        element = await self.get_element()
        return element.to_string()


if __name__ == "__main__":
    grid = MkSpeechBubble("test")
    print(grid)
