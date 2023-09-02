from __future__ import annotations

import logging

from typing import Any
from xml.dom import minidom
from xml.etree import ElementTree

from mknodes import mknav
from mknodes.basenodes import mkbinaryimage, mknode
from mknodes.pages import mkpage
from mknodes.utils import linkprovider, reprhelpers


logger = logging.getLogger(__name__)

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
    root = ElementTree.Element("a")
    if link:
        root.set("href", link)
    card_div = ElementTree.SubElement(root, "div", {"class": "card"})
    container_div = ElementTree.SubElement(
        card_div,
        "div",
        {"class": "showcase-container"},
    )
    ElementTree.SubElement(
        container_div,
        "img",
        src=f"{image}#only-light" if path_dark_mode else image,
        alt=title,
        style=f"width:{size}px,height:{size}px",
    )
    if path_dark_mode:
        ElementTree.SubElement(
            container_div,
            "img",
            src=f"{path_dark_mode}#only-dark",
            alt=title,
            style=f"width:{size}px,height:{size}px",
        )
    if caption:
        overlay_div = ElementTree.SubElement(container_div, "div", {"class": "overlay"})
        overlay_div.text = caption
    p = ElementTree.SubElement(card_div, "p")
    button = ElementTree.SubElement(p, "button")
    button.text = title
    return (
        minidom.parseString(ElementTree.tostring(root))
        .childNodes[0]
        .toprettyxml(indent="   ")
    )
    # return ElementTree.tostring(root, encoding="unicode")


class MkCard(mknode.MkNode):
    """A card node, displaying an image, a button-like label and a hover caption.

    This node requires addtional CSS to work.
    """

    ICON = "material/square-medium"
    STATUS = "new"
    CSS = "css/grid.css"

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
    def url(self) -> str:  # type: ignore[return]
        if not self.target:
            return ""
        if self.associated_project:
            return self.associated_project.linkprovider.get_url(self.target)
        return linkprovider.LinkProvider().get_url(self.target)

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
        files = image.virtual_files()
        path, data = next(iter(files.items()))
        card = MkCard(
            page.title,
            image=path,
            caption=page.subtitle or "",
            target=page,
        )
        card.add_file(path, data)
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
    page = mkpage.MkPage("test", icon="material/puzzle-edit")
    card = MkCard.for_page(page)
    print(card)
