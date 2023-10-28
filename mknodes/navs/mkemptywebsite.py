from __future__ import annotations

from mknodes.navs import mknav
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkEmptyWebsite(mknav.MkNav):
    """Non-populated MkNav which parses given static pages dict."""

    def __init__(self, static_pages: dict | None = None, **kwargs):
        super().__init__(**kwargs)
        import mknodes as mk

        page = self.add_page(is_index=True, title="Overview", hide="toc")
        page += mk.MkText(self.ctx.metadata.description)
        static_pages = static_pages or {}
        self.parse.json(static_pages)


if __name__ == "__main__":
    url = "https://raw.githubusercontent.com/mkdocs/mkdocs/master/docs/getting-started.md"
    doc = MkEmptyWebsite.with_context(static_pages={"Usage": url})
    print(doc)
