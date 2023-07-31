from __future__ import annotations

import logging

from mknodes import mknode, mkpage, project


logger = logging.getLogger(__name__)


class MkLink(mknode.MkNode):
    """A simple Link."""

    def __init__(
        self,
        target: str,
        title: str | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.target = target
        self.title = title

    def _to_markdown(self) -> str:
        match self.target:
            case mkpage.MkPage():
                proj = project.Project()
                path = self.target.resolved_file_path.replace(".md", ".html")
                url = proj.config.site_url + path
            case str() if self.target.startswith(("http:", "https:", "www.")):
                url = self.target
            case str():
                url = f"{self.target}.md"
            case _:
                raise TypeError(self.target)
        title = self.target if self.title is None else self.title
        return f"[{title}]({url})"


if __name__ == "__main__":
    link = MkLink("www.test.de")
