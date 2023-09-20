from __future__ import annotations

from typing import Any, Literal
from xml.etree import ElementTree as Et

from mknodes.basenodes import mkcontainer, mknode
from mknodes.utils import log, reprhelpers, requirements, xmlhelpers


logger = log.get_logger(__name__)


STYLE = (
    "background: linear-gradient(rgba(0, 0, 0, 0), rgba(0, 0, 0,"
    ' 0.4)), url("{image}") center center no-repeat;'
    " background-size: cover;"
)


class MkTimelineItem(mknode.MkNode):
    def __init__(
        self,
        title: str = "",
        content: str | mknode.MkNode = "",
        date: str = "",
        link: str = "",
        button_text: str = "More",
        image: str = "",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.title = title
        self.content = self.to_child_node(content)
        self.image = image
        self.date = date
        self.link = link
        self.button_text = button_text
        self.fade_direction: Literal["left", "right"] | None = None

    @property
    def children(self):
        return [self.content]

    @children.setter
    def children(self, val):
        pass

    def get_element(self):
        root = Et.Element("div", {"class": "timeline-item"})
        timeline_img = Et.SubElement(root, "div", {"class": "timeline-img"})
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
        content_div = Et.SubElement(root, "div", attrs)
        if self.image:
            attrs = {"class": "timeline-img-header"}
            header_div = Et.SubElement(content_div, "div", attrs)
            img = STYLE.format(image=self.image)
            p = Et.SubElement(header_div, "p", {"style": img})
            h_header = Et.SubElement(p, "h2")
        else:
            h_header = Et.SubElement(content_div, "h2")
        h_header.text = self.title
        if self.date:
            div_date = Et.SubElement(content_div, "div", {"class": "date"})
            div_date.text = self.date
        p_text = Et.SubElement(content_div, "p")
        if isinstance(self.content, str):
            p_text.text = self.content
        else:
            text = self.content.to_html()
            p_text.append(Et.fromstring(text))
        if self.link:
            attrs = {"class": "bnt-more", "href": self.link}
            btn = Et.SubElement(content_div, "a", attrs)
            btn.text = self.button_text
        return root


class MkTimeline(mkcontainer.MkContainer):
    """Node to show an Image comparison (using a slider)."""

    ICON = "material/timeline"
    REQUIRED_EXTENSIONS = [
        requirements.Extension("attr_list"),
        requirements.Extension("md_in_html"),
    ]
    JS_FILES = [
        requirements.JSLink("https://code.jquery.com/jquery-2.2.4.min.js"),
        requirements.JSLink(
            "https://cdn.jsdelivr.net/scrollreveal.js/3.3.1/scrollreveal.min.js",
        ),
        requirements.JSFile("js/timeline.js"),
    ]
    CSS = [requirements.CSSFile("css/timeline.css")]
    items: list[MkTimelineItem]

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
        super().__init__(items, **kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(self)

    def _to_markdown(self) -> str:
        root = Et.Element("section", {"class": "timeline"})
        div = Et.SubElement(root, "div", {"class": "container"})
        for i, item in enumerate(self.items):
            item.fade_direction = "left" if i % 2 == 0 else "right"
            elem = item.get_element()
            div.append(elem)
        return "\n\n" + xmlhelpers.pformat(root) + "\n\n"

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkTimeline()
        for i in range(1, 6):
            node += MkTimelineItem(
                title=f"Image card {i}",
                content="A card with an image.",
                date=f"{i} JANUARY 2023",
                link="https://phil65.github.io/mknodes",
                image=f"https://picsum.photos/40{i}",
            )
            admonition = mknodes.MkAdmonition("test")
            node += MkTimelineItem(
                title=f"Card {i}",
                content=admonition,
                date=f"{i} JANUARY 2023",
                link="https://phil65.github.io/mknodes",
            )
        page += node


if __name__ == "__main__":
    import mknodes

    node = mknodes.MkAdmonition("test")
    item = MkTimelineItem(
        title="Title",
        content=node,
        date="1 MAY 2016",
        link="https://phil65.github.io/mknodes",
        # image="https://picsum.photos/1000/800/?random",
    )
    item2 = MkTimelineItem(
        title="Title",
        content="fdsfs",
        date="1 MAY 2016",
        link="https://phil65.github.io/mknodes",
    )
    timeline = MkTimeline([item, item2, item])
    print(timeline.to_html())
