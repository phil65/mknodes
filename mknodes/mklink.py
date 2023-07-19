from __future__ import annotations

import logging

from mknodes import mknode


logger = logging.getLogger(__name__)


class MkLink(mknode.MkNode):
    """A simple Link."""

    def __init__(
        self,
        url: str,
        title: str | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.url = url
        self.title = title

    def _to_markdown(self) -> str:
        suffix = "" if self.url.startswith(("http:", "https:", "www.")) else ".md"
        return f"[{self.url if self.title is None else self.title}]({self.url}{suffix})"


if __name__ == "__main__":
    link = MkLink("www.test.de")
