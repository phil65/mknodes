from __future__ import annotations

from typing import Literal

from mknodes.basenodes import mkcontainer, mknode
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


class MkSpeechBubble(mkcontainer.MkContainer):
    """Node for showing a css-based speech bubble."""

    ICON = "material/chat"
    CSS = "css/speechbubble.css"
    REQUIRED_EXTENSIONS = ["md_in_html"]

    def __init__(
        self,
        content: str | mknode.MkNode | list | None = None,
        arrow: Literal["top", "bottom", "left", "right"] | None = "bottom",
        **kwargs,
    ):
        self.arrow = arrow
        super().__init__(content=content or [], **kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(self, content=self.items, arrow=self.arrow)

    def _to_markdown(self) -> str:
        arrow_str = f" {self.arrow}" if self.arrow else ""
        begin = f'<div class="speech{arrow_str}" markdown="1">\n'
        content = super()._to_markdown()
        end = "\n</div>"
        return f"{begin}{content}{end}"

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkSpeechBubble(MkSpeechBubble.__doc__)
        page += mknodes.MkReprRawRendered(node)
        node = MkSpeechBubble(MkSpeechBubble.__doc__, arrow="left")
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    grid = MkSpeechBubble("test")
    print(grid)
