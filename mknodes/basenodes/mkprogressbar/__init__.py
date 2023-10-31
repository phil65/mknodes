from __future__ import annotations

from typing import Any, Literal

from mknodes.basenodes import mknode
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


class MkProgressBar(mknode.MkNode):
    """Node to display a CSS-based progress bar."""

    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.progressbar")]
    ICON = "fontawesome/solid/bars-progress"
    CSS = [resources.CSSFile("progressbar.css")]
    ATTR_LIST_SEPARATOR = ""

    def __init__(
        self,
        percentage: int,
        *,
        label: str | None | Literal[True] = True,
        style: Literal["thin", "candystripe", "candystripe_animated"] | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            percentage: Percentage value for the progress bar
            label: Label to display on top of progress bar
            style: Progress bar style
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self._label = label
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

    @property
    def label(self) -> str:
        match self._label:
            case str():
                return self._label.format(percentage=self.percentage)
            case True:
                return f"{self.percentage}%"
            case _:
                return ""

    def _to_markdown(self) -> str:
        return rf'[={self.percentage}% "{self.label}"]'

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkProgressBar(60)
        page += mk.MkReprRawRendered(node, header="### Regular")
        node = MkProgressBar(60, style="thin")
        page += mk.MkReprRawRendered(node, header="### Thin")
        node = MkProgressBar(70, style="candystripe", label="We reached {percentage}!")
        page += mk.MkReprRawRendered(node, header="### Candystripe")
        node = MkProgressBar(80, style="candystripe_animated")
        page += mk.MkReprRawRendered(node, header="### Animated")


if __name__ == "__main__":
    bar = MkProgressBar(percentage=30, label=None)
    print(bar)
