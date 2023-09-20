from __future__ import annotations

from typing import Any
from xml.etree import ElementTree

from mknodes.basenodes import mknode
from mknodes.utils import log, reprhelpers, requirements, xmlhelpers


logger = log.get_logger(__name__)


class TimelineItem:
    def __init__(
        self,
        title: str = "",
        content: str = "",
        date: str = "",
        link: str = "",
        image: str = "",
        fade_direction: str | None = None,
    ):
        self.title = title
        self.content = content
        self.image = image
        self.date = date
        self.link = link
        self.fade_direction = fade_direction

    def get_element(self):
        root = ElementTree.Element("div", {"class": "timeline-item"})
        timeline_img = ElementTree.SubElement(root, "div", {"class": "timeline-img"})
        timeline_img.text = " "
        match self.fade_direction:
            case "left":
                fade = " js--fadeInLeft"
            case "right":
                fade = " js--fadeInRight"
            case _:
                fade = ""
        tl = " timeline-card" if self.image else ""
        attrs = {"class": f"timeline-content{tl}{fade}"}
        content_div = ElementTree.SubElement(root, "div", attrs)
        if self.image:
            attrs = {"class": "timeline-img-header"}
            header_div = ElementTree.SubElement(content_div, "div", attrs)
            p = ElementTree.SubElement(
                header_div,
                "p",
                {
                    "style": (
                        "background: linear-gradient(rgba(0, 0, 0, 0), rgba(0, 0, 0,"
                        f' 0.4)), url("{self.image}") center center no-repeat;'
                        " background-size: cover;"
                    ),
                },
            )
            h_header = ElementTree.SubElement(p, "h2")
        else:
            h_header = ElementTree.SubElement(content_div, "h2")
        h_header.text = self.title
        if self.date:
            div_date = ElementTree.SubElement(content_div, "div", {"class": "date"})
            div_date.text = self.date
        p_text = ElementTree.SubElement(content_div, "p")
        p_text.text = self.content
        if self.link:
            attrs = {"class": "bnt-more", "href": self.link}
            btn = ElementTree.SubElement(content_div, "a", attrs)
            btn.text = "More"
        return root


class MkTimeline(mknode.MkNode):
    """Node to show an Image comparison (using a slider)."""

    ICON = "material/timeline"
    REQUIRED_EXTENSIONS = [
        requirements.Extension("attr_list"),
        requirements.Extension("md_in_html"),
    ]
    JS_FILES = [
        requirements.JSFile("js/timeline.js"),
        requirements.JSLink("https://code.jquery.com/jquery-2.2.4.min.js"),
        requirements.JSLink(
            "https://cdn.jsdelivr.net/scrollreveal.js/3.3.1/scrollreveal.min.js",
        ),
    ]
    CSS = [requirements.CSSFile("css/timeline.css")]

    def __init__(
        self,
        items: list | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            items: Timeline items
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.items = items or []

    def __repr__(self):
        return reprhelpers.get_repr(self)

    def _to_markdown(self) -> str:
        root = ElementTree.Element("section", {"class": "timeline"})
        div = ElementTree.SubElement(root, "div", {"class": "container"})
        for item in self.items:
            item = item.get_element()
            div.append(item)
        return "\n\n" + xmlhelpers.pformat(root) + "\n\n"

    @staticmethod
    def create_example_page(page):
        item = TimelineItem(
            title="Title",
            content="A card with an image.",
            date="A label",
            link="https://phil65.github.io/mknodes",
            image="https://picsum.photos/1000/800/?random",
            fade_direction="left",
        )
        item2 = TimelineItem(
            title="Title",
            content="Lorem ipsum dolor sit amet.",
            date="1 MAY 2016",
            link="https://phil65.github.io/mknodes",
            # image="https://picsum.photos/1000/800/?random",
            fade_direction="right",
        )
        node = MkTimeline([item, item2])
        page += node


if __name__ == "__main__":
    item = TimelineItem(
        title="Title",
        content="Lorem ipsum dolor sit amet.",
        date="1 MAY 2016",
        link="https://phil65.github.io/mknodes",
        # image="https://picsum.photos/1000/800/?random",
        fade_direction="left",
    )
    timeline = MkTimeline([item, item, item, item])
    print(timeline.to_markdown())
