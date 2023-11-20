from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mknodes.templatenodes import mktemplate
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


if TYPE_CHECKING:
    from mknodes.info import linkprovider


class MkMaterialBadge(mktemplate.MkTemplate):
    """Node for a CSS-based badge a la MkDocs-Material."""

    ICON = "simple/shieldsdotio"
    CSS = [resources.CSSFile("materialbadge.css")]

    def __init__(
        self,
        icon: str,
        text: str = "",
        *,
        animated: bool = False,
        align_right: bool = False,
        target: linkprovider.LinkableType | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            icon: Icon to display. Can either be an iconify or an emoji slug
            text: Text to display
            animated: Optional animated style
            align_right: Right-align badge
            target: An optional URL / page target for the badge
            kwargs: Keyword arguments passed to parent
        """
        super().__init__("output/html/template", **kwargs)
        self.icon = icon
        self.text = text
        self.animated = animated
        self.align_right = align_right
        self.target = target


if __name__ == "__main__":
    img = MkMaterialBadge("mdi:wrench", "test", align_right=True, animated=True)
    print(img)
