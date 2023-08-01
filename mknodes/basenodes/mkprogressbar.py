from __future__ import annotations

import logging

from typing import Any, Literal

from mknodes.basenodes import mknode


logger = logging.getLogger(__name__)


class MkProgressBar(mknode.MkNode):
    """Node to include other MkPages / Md files."""

    REQUIRED_EXTENSIONS = ["pymdownx.progressbar"]
    ICON = "fontawesome/solid/bars-progress"

    def __init__(
        self,
        percentage: int,
        title: str | None = "{percentage}%",
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
        self.title = title or ""
        self.percentage = percentage
        self.style = style

    def _to_markdown(self) -> str:
        formatted = self.title.format(percentage=self.percentage)
        match self.style:
            case "thin":
                suffix = "{: .thin}"
            case "candystripe":
                suffix = "{: .candystripe}"
            case "candystripe_animated":
                suffix = "{: .candystripe .candystripe-animate}"
            case _:
                suffix = ""
        return rf'[={self.percentage}% "{formatted}"]{suffix}'

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.metadata["status"] = "new"
        page += mknodes.MkAdmonition("MkProgressBar can be used to show a progress bar.")
        page += mknodes.MkDetailsBlock("This Node requires additional css.")
        node = MkProgressBar(60)
        page += node
        page += mknodes.MkCode(str(node), header="Markdown")
        node = MkProgressBar(60, style="thin")
        page += node
        page += mknodes.MkCode(str(node), header="Markdown")
        node = MkProgressBar(70, style="candystripe", title="We reached {percentage}!")
        page += node
        page += mknodes.MkCode(str(node), header="Markdown")
        node = MkProgressBar(80, style="candystripe_animated", title=None)
        page += node
        page += mknodes.MkCode(str(node), header="Markdown")


if __name__ == "__main__":
    bar = MkProgressBar(percentage=30, title=None)
    print(bar)
