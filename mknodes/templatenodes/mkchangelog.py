from __future__ import annotations

import contextlib
import io
import logging
import os

from typing import Any, Literal

from git_changelog import cli

from mknodes.basenodes import mktext
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkChangelog(mktext.MkText):
    """Node for a git-based changelog (created by git-changelog).

    !!! note
        For building a changelog with Github Actions, the actions/checkout@v3
        action needs to have fetch-depth set to 0 (or some other value.)
    """

    ICON = "material/format-list-group"

    def __init__(
        self,
        convention: Literal["basic", "angular", "atom", "conventional"] = "conventional",
        template: Literal["keepachangelog", "angular"] = "keepachangelog",
        sections: list[str] | None = None,
        repository: str | os.PathLike | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            convention: Commit conventions to use
            template: Changelog template
            sections: Which sections to display
            repository: git repo to use for changelog (defaults to current folder)
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.convention = convention
        self.template = template
        self.sections = sections
        self.repository = repository

    def __repr__(self):
        return helpers.get_repr(
            self,
            convention=self.convention,
            template=self.template,
            sections=self.sections,
            repository=self.repository,
            _filter_empty=True,
        )

    @property
    def text(self) -> str:
        with contextlib.redirect_stdout(io.StringIO()):
            _changelog, text = cli.build_and_render(
                repository=str(self.repository) if self.repository else ".",
                template=self.template,
                convention=self.convention,
                parse_refs=True,
                parse_trailers=True,
                sections=self.sections,
            )
        return text

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkChangelog(template="keepachangelog", shift_header_levels=2)
        page += mknodes.MkReprRawRendered(node, header="### keepachangelog template")
        node = MkChangelog(template="angular", shift_header_levels=2)
        page += mknodes.MkReprRawRendered(node, header="### angular template")
        node = MkChangelog(convention="basic", shift_header_levels=2)
        page += mknodes.MkReprRawRendered(node, header="### basic convention")


if __name__ == "__main__":
    changelog = MkChangelog()
    print(changelog)
