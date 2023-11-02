from __future__ import annotations

import os
import tomllib

from typing import Any, Literal
from xml.etree import ElementTree as Et

from mknodes.basenodes import mkcontainer, mknode
from mknodes.utils import log, pathhelpers, reprhelpers, resources, xmlhelpers as xml


logger = log.get_logger(__name__)

SCROLLREVEAL_LINK = (
    "https://cdn.jsdelivr.net/npm/scrollreveal@3.4.0/dist/scrollreveal.min.js"
)
JQUERY_LINK = "https://code.jquery.com/jquery-2.2.4.min.js"

STYLE = (
    "background: linear-gradient(rgba(0, 0, 0, 0), rgba(0, 0, 0,"
    " 0.4)), url({image}) center center no-repeat;"
    " background-size: cover;"
)

SCRIPT = """
window.sr = ScrollReveal();

// Add class to <html> if ScrollReveal is supported
// Note: only works in version 3
if (sr.isSupported()) {
document.documentElement.classList.add('sr');
}
"""


class MkTimelineItem(mknode.MkNode):
    """Single Timeline item / card.

    Not intended to be used directly. Use MkTimeline instead, which manages
    MkTimelineItems.
    """

    def __init__(
        self,
        title: str = "",
        content: str | mknode.MkNode | Et.Element = "",
        *,
        label: str = "",
        link: str = "",
        button_text: str = "More",
        image: str = "",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            title: Item header / title
            content: Text / markdown for the content area
            label: A label, displayed in an upper corner
            link: An optional link for the "More" button
            button_text: allows to switch the button label from "More" to sth user-chosen.
            image: Optional image to display in upper half of the card
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.title = title
        self.content = self.to_child_node(content)
        self.image = image
        self.label = label
        self.link = link
        self.button_text = button_text
        self.fade_direction: Literal["left", "right"] | None = None

    @property
    def children(self):
        return [self.content]

    @children.setter
    def children(self, val):
        pass

    def get_element(self) -> xml.Div:
        root = xml.Div("timeline-item")
        xml.Div("timeline-img", parent=root)
        dct = {"left": " js--fadeInLeft", "right": " js--fadeInRight"}
        fade = dct.get(self.fade_direction or "", "")
        tl = " timeline-card" if self.image else ""
        content_div = xml.Div(f"timeline-content{tl}{fade}", parent=root)
        if self.image:
            style = STYLE.format(image=self.image)
            header_div = xml.Div("timeline-img-header", parent=content_div, style=style)
            p = xml.P(parent=header_div)
            xml.Header(2, self.title, parent=p)
        elif self.title:
            xml.Header(2, self.title, parent=content_div)
        if self.label:
            xml.Div("date", text=self.label, parent=content_div)
        p_text = xml.P(parent=content_div)
        match self.content:
            case str():
                p_text.text = self.content
            case Et.Element():
                p_text.append(self.content)
            case _:
                text = f"<div>{self.content.to_html()}</div>"
                p_text.append(Et.fromstring(text))
        if self.link:
            xml.A("bnt-more", href=self.link, text=self.button_text, parent=content_div)
        return root


class MkTimeline(mkcontainer.MkContainer):
    """Node to show a JavaScript-supported Timeline.

    Consists of cards which slide in and out once they enter / leave the screen.
    """

    ICON = "material/timeline"
    JS_FILES = [
        resources.JSFile(JQUERY_LINK, is_library=True),
        resources.JSFile(SCROLLREVEAL_LINK, is_library=True),
        resources.JSText(SCRIPT, "scrollreveal.js"),  # type: ignore[list-item]
        resources.JSFile("timeline.js"),
    ]
    CSS = [resources.CSSFile("timeline.css")]
    items: list[MkTimelineItem]

    def __init__(
        self,
        items: list | str | os.PathLike | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            items: Timeline items or a path to a TOML file containing timeline data
            kwargs: Keyword arguments passed to parent
        """
        if isinstance(items, str | os.PathLike):
            text = pathhelpers.load_file_cached(str(items))
            data = tomllib.loads(text)
            items = [MkTimelineItem(**step) for step in data.values()]
        elif isinstance(items, dict):
            items = [MkTimelineItem(**step) for step in items.values()]
        super().__init__(items, **kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(self)

    def get_element(self) -> xml.Section:
        root = xml.Section("timeline")
        for i, item in enumerate(self.items):
            item.fade_direction = "left" if i % 2 == 0 else "right"
            elem = item.get_element()
            root.append(elem)
        return root

    def _to_markdown(self) -> str:
        root = self.get_element()
        return "\n\n" + root.to_string() + "\n\n"

    def add_item(
        self,
        title: str = "",
        content: str | mknode.MkNode = "",
        *,
        label: str = "",
        link: str = "",
        button_text: str = "More",
        image: str = "",
        **kwargs: Any,
    ):
        """Add a timeline item.

        title: Item header
        content: Markdown for content
        label: Label to be displayed in small box at the top
        link: Optional button-link. Text of button can be set via button_text
        button_text: Text for the link button.
        image: Optional image for the item
        kwargs: keyword arguments passed to parent
        """
        item = MkTimelineItem(
            title=title,
            content=content,
            label=label,
            link=link,
            button_text=button_text,
            image=image,
            **kwargs,
        )
        self += item
        return item

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkTimeline()
        for i in range(1, 6):
            node += MkTimelineItem(
                title=f"Image card {i}",
                content="A card with an image.",
                label=f"{i} JANUARY 2023",
                link="https://phil65.github.io/mknodes",
                image=f"https://picsum.photos/40{i}",
            )
            admonition = mk.MkAdmonition("test")
            node += MkTimelineItem(
                title=f"Card {i}",
                content=admonition,
                label=f"{i} JANUARY 2023",
                link="https://phil65.github.io/mknodes",
            )
        page += node


if __name__ == "__main__":
    import mknodes as mk

    node = mk.MkAdmonition("test")
    item = MkTimelineItem(
        title="Title",
        content=node,
        label="1 MAY 2016",
        link="https://phil65.github.io/mknodes",
        # image="https://picsum.photos/1000/800/?random",
    )
    item2 = MkTimelineItem(
        title="Title",
        content="fdsfs",
        label="1 MAY 2016",
        link="https://phil65.github.io/mknodes",
    )
    timeline = MkTimeline([item, item2, item])
