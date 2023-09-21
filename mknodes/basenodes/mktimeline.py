from __future__ import annotations

from typing import Any, Literal
from xml.etree import ElementTree as Et

from mknodes.basenodes import mkcontainer, mknode
from mknodes.utils import log, reprhelpers, requirements, xmlhelpers as xml


logger = log.get_logger(__name__)

SCROLLREVEAL_LINK = "https://cdn.jsdelivr.net/scrollreveal.js/3.3.1/scrollreveal.min.js"
JQUERY_LINK = "https://code.jquery.com/jquery-2.2.4.min.js"

STYLE = (
    "background: linear-gradient(rgba(0, 0, 0, 0), rgba(0, 0, 0,"
    " 0.4)), url({image}) center center no-repeat;"
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

    def get_element(self) -> xml.Div:
        root = xml.Div("timeline-item")
        xml.Div("timeline-img", parent=root)
        match self.fade_direction:
            case "left":
                fade = " js--fadeInLeft"
            case "right":
                fade = " js--fadeInRight"
            case _:
                fade = ""
        tl = " timeline-card" if self.image else ""
        content_div = xml.Div(f"timeline-content{tl}{fade}", parent=root)
        if self.image:
            style = STYLE.format(image=self.image)
            header_div = xml.Div("timeline-img-header", parent=content_div, style=style)
            p = xml.P(parent=header_div)
            xml.Header(2, self.title, parent=p)
        elif self.title:
            xml.Header(2, self.title, parent=content_div)
        if self.date:
            xml.Div("date", text=self.date, parent=content_div)
        p_text = xml.P(parent=content_div)
        if isinstance(self.content, str):
            p_text.text = self.content
        else:
            text = f"<div>{self.content.to_html()}</div>"
            p_text.append(Et.fromstring(text))
        if self.link:
            xml.A("bnt-more", href=self.link, text=self.button_text, parent=content_div)
        return root


class MkTimeline(mkcontainer.MkContainer):
    """Node to show an Image comparison (using a slider)."""

    ICON = "material/timeline"
    REQUIRED_EXTENSIONS = [
        requirements.Extension("attr_list"),
        requirements.Extension("md_in_html"),
    ]
    JS_FILES = [
        requirements.JSLink(JQUERY_LINK),
        requirements.JSLink(SCROLLREVEAL_LINK),
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
        root = xml.Section("timeline")
        div = xml.Div("container", parent=root)
        for i, item in enumerate(self.items):
            item.fade_direction = "left" if i % 2 == 0 else "right"
            elem = item.get_element()
            div.append(elem)
        return "\n\n" + root.to_string() + "\n\n"

    def add_item(
        self,
        title: str = "",
        content: str | mknode.MkNode = "",
        date: str = "",
        link: str = "",
        button_text: str = "More",
        image: str = "",
        **kwargs,
    ):
        item = MkTimelineItem(
            title=title,
            content=content,
            date=date,
            link=link,
            button_text=button_text,
            image=image,
            **kwargs,
        )
        self += item
        return item

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
