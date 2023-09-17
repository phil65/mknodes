from __future__ import annotations

import types

from typing import TYPE_CHECKING, Any

from mknodes.basenodes import mknode
from mknodes.utils import log, reprhelpers


if TYPE_CHECKING:
    from mknodes.navs import mknav
    from mknodes.pages import mkpage

logger = log.get_logger(__name__)


class MkLink(mknode.MkNode):
    """A simple Link (with optional icon and option to show up as a button)."""

    ICON = "octicons/link-24"
    REQUIRED_EXTENSIONS = ["attr_list"]  # for buttons

    def __init__(
        self,
        target: str | mkpage.MkPage | mknav.MkNav | type | types.ModuleType,
        title: str | None = None,
        icon: str | None = None,
        as_button: bool = False,
        primary_color: bool = False,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            target: Link target
            title: Title used for link
            icon: Optional icon to be displayed in front of title
            as_button: Whether link should be rendered as button
            primary_color: If rendered as button, use primary color as background.
            kwargs: keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.target = target
        self.title = title
        self.as_button = as_button
        self.primary_color = primary_color
        self._icon = icon or ""
        if as_button:
            self.add_css_class("md-button")
        if primary_color:
            self.add_css_class("md-button--primary")

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            target=self.target,
            title=self.title,
            icon=self._icon,
            as_button=self.as_button,
            primary_color=self.primary_color,
            _filter_empty=True,
            _filter_false=True,
        )

    @property
    def icon(self):
        if not self._icon or self._icon.startswith(":"):
            return self._icon
        icon = self._icon if "/" in self._icon else f"material/{self._icon}"
        return f':{icon.replace("/", "-")}:'

    @property
    def url(self) -> str:
        return self.ctx.links.get_url(self.target)

    def _to_markdown(self) -> str:
        title = self.target if self.title is None else self.title
        prefix = f"{self.icon} " if self.icon else ""
        return f"[{prefix}{title}]({self.url})"

    @staticmethod
    def create_example_page(page):
        import mknodes

        url = "http://www.google.de"
        node = mknodes.MkLink(url, "This is a link.")
        page += mknodes.MkReprRawRendered(node, header="### Regular")
        node = mknodes.MkLink(url, "Disguised as button.", as_button=True)
        page += mknodes.MkReprRawRendered(node, header="### Button")
        node = mknodes.MkLink(url, "Colored.", as_button=True, primary_color=True)
        page += mknodes.MkReprRawRendered(node, header="### Colored")
        node = mknodes.MkLink(url, "With icon.", icon="octicons/link-24")
        page += mknodes.MkReprRawRendered(node, header="### With icon")
        node = mknodes.MkLink(page.parent.index_page, "To page.")
        page += mknodes.MkReprRawRendered(node, header="###To page")


if __name__ == "__main__":
    link = MkLink("www.test.de")
