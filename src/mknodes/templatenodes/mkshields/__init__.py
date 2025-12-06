from __future__ import annotations

from typing import Any, TYPE_CHECKING

from mknodes.basenodes import mkcontainer, mkimage
from mknodes.data import badges
from mknodes.utils import log

if TYPE_CHECKING:
    from mknodes.basenodes import mknode
    from collections.abc import Sequence


logger = log.get_logger(__name__)


class MkShields(mkcontainer.MkContainer):
    """Container for Shields.io / GitHub badges."""

    ICON = "simple/shieldsdotio"
    VIRTUAL_CHILDREN = True
    ATTR_LIST_SEPARATOR = ""

    def __init__(
        self,
        shields: Sequence[badges.BadgeTypeStr] | None = None,
        *,
        user: str | None = None,
        project: str | None = None,
        branch: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            shields: Shields to include
            user: Github username for shields
            project: project name for shields
            branch: branch name for shields
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.block_separator = "\n"
        self._user = user
        self._project = project
        self._branch = branch
        self._shields = shields

    @property
    def user(self) -> str:
        match self._user:
            case None:
                return self.ctx.metadata.repository_username
            case str():
                return self._user
            case _:
                msg = "Invalid user type"
                raise ValueError(msg)

    @user.setter
    def user(self, val: str | None) -> None:
        self._user = val

    @property
    def project(self) -> str:
        if isinstance(self._project, str):
            return self._project
        return self.ctx.metadata.repository_name

    @project.setter
    def project(self, value) -> None:
        self._project = value

    @property
    def shields(self):
        shields = self._shields or [i.identifier for i in badges.SHIELDS]
        return [s for s in badges.SHIELDS if s.identifier in shields]

    @property
    def branch(self) -> str:
        if isinstance(self._branch, str):
            return self._branch
        return self.ctx.git.main_branch or "main"

    def get_items(self) -> list[mknode.MkNode]:
        """Return computed shield items."""
        return [
            mkimage.MkImage(
                s.get_image_url(user=self.user, project=self.project, branch=self.branch),
                target=s.get_url(user=self.user, project=self.project),
                title=s.title,
                parent=self,
            )
            for s in self.shields
        ]

    def set_items(self, items: list[mknode.MkNode]) -> None:
        """Set items (no-op for computed shields)."""


if __name__ == "__main__":
    shields = MkShields(shields=["version", "status", "codecov"], user="phil65", project="prettyqt")
    print(shields)
