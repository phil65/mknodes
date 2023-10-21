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
        page += mk.MkText(r"metadata.description", is_jinja_expression=True)
        static_pages = static_pages or {}
        self.parse.json(static_pages)

    @classmethod
    def for_project(cls, project, **kwargs):
        root = cls(context=project.context, **kwargs)
        project.set_root(root)
        return root


if __name__ == "__main__":
    import mknodes as mk

    theme = mk.MaterialTheme()
    doc = MkEmptyWebsite.for_project(
        mk.Project(theme=theme),
        static_pages={
            "Usage": "https://raw.githubusercontent.com/mkdocs/mkdocs/master/docs/getting-started.md",
        },
    )
    print(doc)
