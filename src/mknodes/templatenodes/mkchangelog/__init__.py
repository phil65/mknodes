import contextlib
import functools
import io
import threading

from typing import Any, Literal, TYPE_CHECKING

import git_changelog

from mknodes import inputs
from mknodes.basenodes import mktext
from mknodes.utils import helpers, log, resources

if TYPE_CHECKING:
    import os


logger = log.get_logger(__name__)


_LOCK = threading.Lock()


@helpers.list_to_tuple
@functools.cache
def get_changelog(
    repository: str,
    template: str,
    convention: str,
    sections: tuple[str, ...] | None = None,
    filter_commits: str | None = None,
) -> str:
    """Get changelog formatted as markdown.

    Args:
        repository: Path to the git repository to get a changelog for
        template: Which template to use
        convention: Which changelog convention to apply
        sections: Optionally filter sections
        filter_commits: The Git revision-range used to filter commits in git-log.
    """
    # git-changelog writes to `sys.stdout` (swapped by redirect_stdout, process-wide):
    # one changelog at a time, the resolve phase builds them in worker threads.
    with _LOCK, contextlib.redirect_stdout(io.StringIO()):
        try:
            _changelog, text = git_changelog.build_and_render(
                repository=repository,
                template=template,
                convention=convention,
                parse_refs=True,
                parse_trailers=True,
                filter_commits=filter_commits,
                sections=list(sections) if sections else None,
            )
        except ValueError:
            # try without commit range
            _changelog, text = git_changelog.build_and_render(
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
        For building a changelog with Github Actions, the actions/checkout@v4
        action needs to have fetch-depth set to 0 (or some other value.)
    """

    ICON = "material/format-list-group"
    REQUIRED_PACKAGES = [resources.Package("git-changelog")]

    def __init__(
        self,
        convention: Literal["basic", "angular", "atom", "conventional"] = "conventional",
        template: Literal["keepachangelog", "angular"] = "keepachangelog",
        sections: list[str] | None = None,
        repository: str | os.PathLike[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
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

    @property
    def repository(self):
        match self._repository:
            case None:
                return self.ctx.metadata.repository_path
            case _:
                return self._repository

    def _changelog_params(self) -> dict[str, Any]:
        filter_commits = None
        if self._repository is None and (
            cfg := self.ctx.metadata.pyproject_file.tool.get("git-changelog")
        ):
            filter_commits = cfg.get("filter-commits")
        return dict(
            repository=str(self.repository),
            template=self.template,
            convention=self.convention,
            sections=list(self.sections) if self.sections else None,
            filter_commits=filter_commits,
        )

    def get_input_requests(self) -> list[inputs.InputRequest]:
        return [inputs.InputRequest.create("changelog", **self._changelog_params())]

    def get_text(self) -> str:
        return self.ctx.inputs.get("changelog", **self._changelog_params())


if __name__ == "__main__":
    changelog = MkChangelog()
    print(changelog)
