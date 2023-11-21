from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mknodes.basenodes import mkbinaryimage
from mknodes.templatenodes import mktemplate
from mknodes.utils import log, resources


if TYPE_CHECKING:
    from mknodes.info import linkprovider
    from mknodes.pages import mkpage


logger = log.get_logger(__name__)

CARD_DEFAULT_SIZE = 200


class MkCard(mktemplate.MkTemplate):
    """A card node, displaying an image, a button-like label and a hover caption.

    This node requires addtional CSS to work.
    """

    ICON = "material/square-medium"
    STATUS = "new"
    CSS = [resources.CSSFile("grid.css")]

    def __init__(
        self,
        title: str,
        image: str,
        *,
        caption: str | None = None,
        target: linkprovider.LinkableType | None = None,
        size: int = CARD_DEFAULT_SIZE,
        path_dark_mode: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            title: Button text
            image: Card image
            caption: Image caption
            target: Link target. Can be a URL, an MkPage, or an MkNav
            size: Height/Width of the card
            path_dark_mode: Optional alternative image for dark mode
            kwargs: keyword arguments passed to parent
        """
        super().__init__("output/markdown/template", **kwargs)
        self.target = target
        self.title = title
        self.image = image
        self.caption = caption
        self.size = size
        self.path_dark_mode = path_dark_mode

    @classmethod
    def for_page(cls, page):
        image = mkbinaryimage.MkBinaryImage.for_icon(page.icon)
        card = MkCard(
            page.title,
            image=image.path,
            caption=page.subtitle or "",
            target=page,
        )
        card.add_file(image.path, image.data)
        return card


if __name__ == "__main__":
    from mknodes.pages import mkpage

    page = mkpage.MkPage("test", icon="material/puzzle-edit")
    card = MkCard.for_page(page)
    print(card)
