from __future__ import annotations

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import icons, log, reprhelpers, resources, xmlhelpers as xml


logger = log.get_logger(__name__)


class MkMaterialBadge(mknode.MkNode):
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
        link: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            icon: Icon to display
            text: Text to display
            animated: Optional animated style
            align_right: Right-align badge
            link: An optional link for the badge
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.icon = icon
        self.text = text
        self.animated = animated
        self.align_right = align_right
        self.link = link

    def _to_markdown(self):
        classes = "md-typeset mdx-badge"
        if self.animated:
            classes += " mdx-badge--heart"
        if self.align_right:
            classes += " mdx-badge--right"
        root = xml.Span(classes)
        if self.icon:
            icon = icons.get_emoji_slug(self.icon)
            xml.Span("mdx-badge__icon", parent=root, text=icon)
        if self.text:
            xml.Span("mdx-badge__text", parent=root, text=self.text)
        return root.to_string()

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            icon=self.icon,
            text=self.text,
            animated=self.animated,
            align_right=self.align_right,
            link=self.link,
            _filter_empty=True,
        )

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        icon = ":mdi-file:"
        node = MkMaterialBadge(icon, text="text")
        page += mk.MkReprRawRendered(node)

        node = MkMaterialBadge(icon, text="text", align_right=True)
        page += mk.MkReprRawRendered(node)

        node = MkMaterialBadge(icon, text="text", animated=True)
        page += mk.MkReprRawRendered(node)

        node = MkMaterialBadge(icon, text="text", animated=True, align_right=True)
        page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    img = MkMaterialBadge("mdi:wrench", "test", align_right=True, animated=True)
    print(img)
