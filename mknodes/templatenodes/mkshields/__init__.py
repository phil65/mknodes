from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from mknodes.basenodes import mkcontainer, mkimage, mknode
from mknodes.data import badges
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkShields(mkcontainer.MkContainer):
    """Container for Shields.io / GitHub badges."""

    ICON = "simple/shieldsdotio"
    VIRTUAL_CHILDREN = True

    def __init__(
        self,
        shields: Sequence[badges.BadgeTypeStr] | None = None,
        *,
        user: str | None = None,
        project: str | None = None,
        branch: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
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
    def user(self):
        match self._user:
            case None:
                return self.ctx.metadata.repository_username
            case str():
                return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def project(self):
        if isinstance(self._project, str):
            return self._project
        return self.ctx.metadata.repository_name

    @project.setter
    def project(self, value):
        self._project = value

    @property
    def shields(self):
        return self._shields or [i.identifier for i in badges.SHIELDS]

    @property
    def branch(self) -> str:
        if isinstance(self._branch, str):
            return self._branch
        return self.ctx.git.main_branch or "main"

    @property
    def items(self) -> list[mknode.MkNode]:
        return [
            mkimage.MkImage(
                s.get_image_url(user=self.user, project=self.project, branch=self.branch),
                target=s.get_url(user=self.user, project=self.project),
                title=s.title,
                parent=self,
            )
            for s in badges.SHIELDS
            if s.identifier in self.shields
        ]

    @items.setter
    def items(self, value):
        pass

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkShields(["version", "status", "codecov"])
        page += mk.MkReprRawRendered(node)
        node = MkShields(user="phil65", project="mknodes")
        page += mk.MkReprRawRendered(node)
        node = MkShields(user="mkdocs", project="mkdocs")
        page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    shields = MkShields(
        shields=["version", "status", "codecov"],
        user="phil65",
        project="prettyqt",
    )
    print(shields)
