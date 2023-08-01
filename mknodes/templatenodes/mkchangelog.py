from __future__ import annotations

import contextlib
import io
import logging
import os

from typing import Any, Literal

from git_changelog import cli

from mknodes.basenodes import mknode


logger = logging.getLogger(__name__)


class MkChangelog(mknode.MkNode):
    """Git-based changelog (created by git-changelog).

    !!! note
        For building a changelog with Github Actions, the actions/checkout@v3
        action needs to have fetch-depth set to 0 (or some other value.)
    """

    ICON = "material/format-list-group"

    def __init__(
        self,
        convention: Literal["basic", "angular", "atom", "conventional"] = "angular",
        template: Literal["keepachangelog", "angular"] = "keepachangelog",
        parse_refs: bool = True,
        parse_trailers: bool = True,
        sections: list[str] | None = None,
        repository: str | os.PathLike = ".",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            convention: Commit conventions to use
            template: Changelog template
            parse_refs: Whether to parse References
            parse_trailers: Whether to parse Github Trailers
            sections: Which sections to display
            repository: git repo to use for changelog (defaults to current folder)
            kwargs: Keyword arguments passed to parent
        """
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

        page.metadata["status"] = "new"
        node = MkChangelog()
        page += node
        page += mknodes.MkHtmlBlock(str(node), header="Markdown")


if __name__ == "__main__":
    changelog = MkChangelog()
    print(changelog)
