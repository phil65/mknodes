from __future__ import annotations

from collections.abc import Sequence
import logging

from typing import Any

from mknodes.basenodes import mkcontainer, mkimage, mknode
from mknodes.data import badges
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkShields(mkcontainer.MkContainer):
    """MkCritic block."""

    ICON = "simple/shieldsdotio"

    def __init__(
        self,
        shields: Sequence[badges.BadgeTypeStr] | None,
        user: str | None = None,
        project: str | None = None,
        branch: str = "main",
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
        self.user = user
        self.project = project
        self.branch = branch
        self.shields = shields

    def __repr__(self):
        kwargs = dict(
            shields=self.shields,
            user=self.user,
            project=self.project,
            _filter_empty=True,
        )
        if self.branch != "main":
            kwargs["branch"] = self.branch
        return helpers.get_repr(self, **kwargs)

    @property
    def items(self) -> list[mknode.MkNode]:
        match self.user:
            case None if self.associated_project:
                user = self.associated_project.get_repository_username()
            case None:
                user = ""
            case str():
                user = self.user
        match self.project:
            case None if self.associated_project:
                project = self.associated_project.get_repository_name()
            case None:
                project = ""
            case str():
                project = self.project
        shields = self.shields or [i.identifier for i in badges.SHIELDS]
        return [
            mkimage.MkImage(
                s.get_image_url(user=user, project=project, branch=self.branch),
                link=s.get_url(user=user, project=project),
                title=s.title,
                parent=self,
            )
            for s in badges.SHIELDS
            if s.identifier in shields
        ]

    @items.setter
    def items(self, value):
        pass

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkShields(shields=["version", "status", "codecov"])
        page += mknodes.MkReprRawRendered(node)
        node = MkShields(user="phil65", project="mknodes", shields=None)
        page += mknodes.MkReprRawRendered(node)
        node = MkShields(user="mkdocs", project="mkdocs", shields=None)
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    shields = MkShields(
        shields=["version", "status", "codecov"],
        user="phil65",
        project="prettyqt",
    )
    print(shields)
