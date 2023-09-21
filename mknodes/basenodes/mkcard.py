from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mknodes.basenodes import mkbinaryimage, mknode
from mknodes.utils import log, reprhelpers, requirements, xmlhelpers as xml


if TYPE_CHECKING:
    from mknodes.navs import mknav
    from mknodes.pages import mkpage


logger = log.get_logger(__name__)

CARD_DEFAULT_SIZE = 200


def build_html_card(
    *,
    image: str,
    title: str,
    link: str | None = None,
    size: int = CARD_DEFAULT_SIZE,
    caption: str | None = None,
    path_dark_mode: str | None = None,
):
    root = xml.A(href=link)
    card_div = xml.Div("card", parent=root)
    container_div = xml.Div("showcase-container", parent=card_div)
    src = f"{image}#only-light" if path_dark_mode else image
    style = f"width:{size}px,height:{size}px"
    xml.Img(parent=container_div, src=src, alt=title, style=style)
    if path_dark_mode:
        src = f"{path_dark_mode}#only-dark"
        style = f"width:{size}px,height:{size}px"
        xml.Img(parent=container_div, src=src, alt=title, style=style)
    if caption:
        xml.Div("overlay", text=caption, parent=container_div)
    p = xml.P(parent=card_div)
    button = xml.Button(parent=p)
    button.text = title
    return root.to_string()


class MkCard(mknode.MkNode):
    """A card node, displaying an image, a button-like label and a hover caption.

    This node requires addtional CSS to work.
    """

    ICON = "material/square-medium"
    STATUS = "new"
    CSS = [requirements.CSSFile("css/grid.css")]

    def __init__(
        self,
        title: str,
        image: str,
        caption: str | None = None,
        target: str | mkpage.MkPage | mknav.MkNav | None = None,
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
        super().__init__(**kwargs)
        self.target = target
        self.title = title
        self.image = image
        self.caption = caption
        self.size = size
        self.path_dark_mode = path_dark_mode

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            title=self.title,
            image=self.image,
            caption=self.caption,
            target=self.target,
            size=self.size if self.size != CARD_DEFAULT_SIZE else None,
            path_dark_mode=self.path_dark_mode,
            _filter_empty=True,
        )

    @property
    def url(self) -> str:
        return self.ctx.links.get_url(self.target) if self.target else ""

    def _to_markdown(self) -> str:
        return build_html_card(
            title=self.title,
            image=self.image,
            caption=self.caption,
            link=self.url,
            size=self.size,
            path_dark_mode=self.path_dark_mode,
        )

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

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkCard(
            image="https://picsum.photos/300",
            title="Title",
            target="https://phil65.github.io/mknodes/",
        )
        page += mknodes.MkReprRawRendered(node, header="### Without caption")

        node = MkCard(
            image="https://picsum.photos/300",
            title="Title",
            target="https://phil65.github.io/mknodes/",
            caption="Caption",
        )
        page += mknodes.MkReprRawRendered(node, header="### With caption")

        node = MkCard(
            image="https://picsum.photos/300",
            title="Title",
            path_dark_mode="https://picsum.photos/200",
        )
        page += mknodes.MkReprRawRendered(node, header="### Separate dark mode image")


if __name__ == "__main__":
    from mknodes.pages import mkpage

    page = mkpage.MkPage("test", icon="material/puzzle-edit")
    card = MkCard.for_page(page)
    print(card)
