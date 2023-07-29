from __future__ import annotations

import contextlib
import io
import logging
import os

from typing import Literal

from git_changelog import cli

from mknodes import mknode


logger = logging.getLogger(__name__)


class MkChangelog(mknode.MkNode):
    """Git-based changelog (created by git-changelog)."""

    def __init__(
        self,
        repository: str | os.PathLike,
        convention: Literal["angular", "atom"] = "angular",
        template: Literal["keepachangelog", "angular"] = "keepachangelog",
        parse_refs: bool = True,
        parse_trailers: bool = True,
        sections: list[str] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.repository = repository
        self.convention = convention
        self.template = template
        self.parse_trailers = parse_trailers
        self.parse_refs = parse_refs
        self.sections = sections

    def _to_markdown(self) -> str:
        with contextlib.redirect_stdout(io.StringIO()):
            _changelog, text = cli.build_and_render(
                repository=str(self.repository),
                template=self.template,
                convention=self.convention,
                parse_refs=self.parse_refs,
                parse_trailers=self.parse_trailers,
                sections=self.sections,
            )
        return text

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkChangelog(repository=".")
        page += node
        page += mknodes.MkHtmlBlock(str(node), header="Markdown")


if __name__ == "__main__":
    installguide = MkChangelog(repository=".")
    print(installguide)
