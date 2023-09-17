from __future__ import annotations

from typing import Any, Literal

from mknodes.basenodes import mknode
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


class MkProgressBar(mknode.MkNode):
    """Node to display a CSS-based progress bar."""

    REQUIRED_EXTENSIONS = ["pymdownx.progressbar"]
    ICON = "fontawesome/solid/bars-progress"
    STATUS = "new"
    CSS = "css/progressbar.css"

    def __init__(
        self,
        percentage: int,
        title: str | None | Literal[True] = True,
        style: Literal["thin", "candystripe", "candystripe_animated"] | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            percentage: Percentage value for the progress bar
            title: Title to display on top of progress bar
            style: Progress bar style
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.title = title
        self.percentage = percentage
        self.style = style
        match self.style:
            case "thin":
                self.add_css_class("thin")
            case "candystripe":
                self.add_css_class("candystripe")
            case "candystripe_animated":
                self.add_css_class("candystripe")
                self.add_css_class("candystripe-animate")

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            percentage=self.percentage,
            title=self.title,
            style=self.style,
        )

    def _to_markdown(self) -> str:
        match self.title:
            case None:
                title = ""
            case str():
                title = self.title.format(percentage=self.percentage)
            case True:
                title = f"{self.percentage}%"
        return rf'[={self.percentage}% "{title}"]'

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkProgressBar(60)
        page += mknodes.MkReprRawRendered(node, header="### Regular")
        node = MkProgressBar(60, style="thin")
        page += mknodes.MkReprRawRendered(node, header="### Thin")
        node = MkProgressBar(70, style="candystripe", title="We reached {percentage}!")
        page += mknodes.MkReprRawRendered(node, header="### Candystripe")
        node = MkProgressBar(80, style="candystripe_animated")
        page += mknodes.MkReprRawRendered(node, header="### Animated")


if __name__ == "__main__":
    bar = MkProgressBar(percentage=30, title=None)
    print(bar)
