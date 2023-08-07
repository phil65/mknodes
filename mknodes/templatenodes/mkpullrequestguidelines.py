from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mkcode, mkcontainer, mktext


logger = logging.getLogger(__name__)


INTRO = """Link to any related issue in the Pull Request message.

During the review, we recommend using fixups:"""

SQUASH_TEXT = "Once all the changes are approved, you can squash your commits:"

OUTRO = """If this seems all too complicated, you can push or force-push each new commit,
and we will squash them ourselves if needed, before merging.
"""


class MkPullRequestGuidelines(mkcontainer.MkContainer):
    """Pull request guide text."""

    ICON = "octicons/git-pull-request-24"

    def __init__(
        self,
        header: str = "Pull request guidelines",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header=header, **kwargs)

    @property
    def items(self):
        return [
            mktext.MkText(INTRO, parent=self),
            mkcode.MkCode(
                "git commit --fixup=SHA # SHA of commit you want to fix",
                language="bash",
                parent=self,
            ),
            mktext.MkText(SQUASH_TEXT, parent=self),
            mkcode.MkCode(
                "git rebase -i --autosquash main",
                language="bash",
                parent=self,
            ),
            mktext.MkText("And force-push:", parent=self),
            mkcode.MkCode("git push -f", language="bash", parent=self),
            mktext.MkText(OUTRO, parent=self),
        ]

    @items.setter
    def items(self, value):
        pass

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.status = "new"  # for the small icon in the left menu
        node = MkPullRequestGuidelines()
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    guideline = MkPullRequestGuidelines()
    print(guideline)
