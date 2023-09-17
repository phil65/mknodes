from __future__ import annotations

from mknodes.navs import mknav
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkEmptyWebsite(mknav.MkNav):
    """Nav for showing a module documenation."""

    def __init__(self, static_pages=None, **kwargs):
        super().__init__(**kwargs)
        import mknodes

        page = self.add_index_page("Overview", hide="toc")
        page += mknodes.MkText(r"metadata.description", is_jinja_expression=True)
        static_pages = static_pages or {}
        self.parse.json(static_pages)

    @classmethod
    def for_project(cls, project, **kwargs):
        root = cls(project=project, **kwargs)
        project.set_root(root)
        return root


if __name__ == "__main__":
    import mknodes

    doc = MkEmptyWebsite.for_project(
        mknodes.Project.for_mknodes(),
        static_pages={
            "Usage": "https://raw.githubusercontent.com/mkdocs/mkdocs/master/docs/getting-started.md",
        },
    )
    print(doc)
