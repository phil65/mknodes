from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mknodes.basenodes import mknode
from mknodes.utils import icons, log


if TYPE_CHECKING:
    from mknodes.info import linkprovider

logger = log.get_logger(__name__)


class MkLink(mknode.MkNode):
    """A simple Link (with optional icon and option to show up as a button).

    If no title is given, the URL is used as a title.
    """

    ICON = "octicons/link-24"
    ATTR_LIST_SEPARATOR = ""

    def __init__(
        self,
        target: linkprovider.LinkableType,
        title: str | None = None,
        *,
        tooltip: str | None = None,
        icon: str | None = None,
        as_button: bool = False,
        primary_color: bool = False,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            target: Link target
            title: Title used for link
            tooltip: Tooltip for the link
            icon: Optional icon to be displayed in front of title
            as_button: Whether link should be rendered as button
            primary_color: If rendered as button, use primary color as background.
            kwargs: keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.target = target
        self._title = title
        self.tooltip = tooltip
        self.as_button = as_button
        self.primary_color = primary_color
        self._icon = icon
        if as_button:
            self.add_css_class("md-button")
        if primary_color:
            self.add_css_class("md-button--primary")

    @property
    def icon(self) -> str:
        return icons.get_emoji_slug(self._icon) if self._icon else ""

    @property
    def url(self) -> str:
        return self.ctx.links.get_url(self.target)

    @property
    def title(self) -> str:
        return self._title or self.url

    def _to_markdown(self) -> str:
        prefix = f"{self.icon} " if self.icon else ""
        tooltip = f" {self.tooltip!r}" if self.tooltip else ""
        return f"[{prefix}{self.title}]({self.url}{tooltip})"

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        url = "http://www.google.de"
        node = mk.MkLink(url, "This is a link.")
        page += mk.MkReprRawRendered(node, header="### Regular")
        node = mk.MkLink(url, "Disguised as button.", as_button=True)
        page += mk.MkReprRawRendered(node, header="### Button")
        node = mk.MkLink(url, "Colored.", as_button=True, primary_color=True)
        page += mk.MkReprRawRendered(node, header="### Colored")
        node = mk.MkLink(url, "With icon.", icon="octicons/link-24")
        page += mk.MkReprRawRendered(node, header="### With icon")
        node = mk.MkLink(url, "With tooltip.", tooltip="Test")
        page += mk.MkReprRawRendered(node, header="### With tooltip")
        node = mk.MkLink(page.parent.index_page, "To page.")
        page += mk.MkReprRawRendered(node, header="###To page")


if __name__ == "__main__":
    link = MkLink("www.test.de")
