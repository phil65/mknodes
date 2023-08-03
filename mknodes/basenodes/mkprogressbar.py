from __future__ import annotations

import logging

from typing import Any, Literal

from mknodes.basenodes import mknode
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkProgressBar(mknode.MkNode):
    """Node to include other MkPages / Md files."""

    REQUIRED_EXTENSIONS = ["pymdownx.progressbar"]
    ICON = "fontawesome/solid/bars-progress"

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

    def __repr__(self):
        return helpers.get_repr(
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
        match self.style:
            case "thin":
                suffix = "{: .thin}"
            case "candystripe":
                suffix = "{: .candystripe}"
            case "candystripe_animated":
                suffix = "{: .candystripe .candystripe-animate}"
            case _:
                suffix = ""
        return rf'[={self.percentage}% "{title}"]{suffix}'

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.status = "new"  # for the small icon in the left menu
        page += mknodes.MkAdmonition("MkProgressBar can be used to show a progress bar.")
        page += mknodes.MkDetailsBlock("This Node requires additional css.")
        node = MkProgressBar(60)
        page += mknodes.MkReprRawRendered(node)
        node = MkProgressBar(60, style="thin")
        page += mknodes.MkReprRawRendered(node)
        node = MkProgressBar(70, style="candystripe", title="We reached {percentage}!")
        page += mknodes.MkReprRawRendered(node)
        node = MkProgressBar(80, style="candystripe_animated", title=None)
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    bar = MkProgressBar(percentage=30, title=None)
    print(bar)
