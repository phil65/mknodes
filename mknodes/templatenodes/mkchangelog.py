from __future__ import annotations

import contextlib
import functools
import io
import logging
import os

from typing import Any, Literal

from git_changelog import cli

from mknodes.basenodes import mktext
from mknodes.utils import reprhelpers


logger = logging.getLogger(__name__)


@functools.cache
def get_changelog(
    repository: str,
    template: str,
    convention: str,
    sections: tuple[str, ...] | None = None,
) -> str:
    with contextlib.redirect_stdout(io.StringIO()):
        _changelog, text = cli.build_and_render(
            repository=repository,
            template=template,
            convention=convention,
            parse_refs=True,
            parse_trailers=True,
            sections=list(sections) if sections else None,
        )
    return text


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
        self._repository = repository

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            convention=self.convention,
            template=self.template,
            sections=self.sections,
            repository=self.repository,
            _filter_empty=True,
        )

    @property
    def repository(self):
        match self._repository:
            case None if self.associated_project:
                return str(self.associated_project.folderinfo.path)
            case None:
                return "."
            case _:
                return str(self._repository)

    @property
    def text(self) -> str:
        return get_changelog(
            repository=self.repository,
            template=self.template,
            convention=self.convention,
            sections=tuple(self.sections) if self.sections else None,
        )

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
