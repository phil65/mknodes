from __future__ import annotations

from typing import Literal

from mknodes.basenodes import mkcontainer, mknode
from mknodes.utils import log, resources, xmlhelpers as xml


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
        **kwargs,
    ):
        self.arrow = arrow
        super().__init__(content=content or [], **kwargs)

    def get_element(self) -> xml.Div:
        klass = f"speech {self.arrow}" if self.arrow else "speech"
        root = xml.Div(klass, markdown=True)
        root.text = "\n" + super()._to_markdown() + "\n"
        return root

    def _to_markdown(self) -> str:
        return self.get_element().to_string()


if __name__ == "__main__":
    grid = MkSpeechBubble("test")
    print(grid)
