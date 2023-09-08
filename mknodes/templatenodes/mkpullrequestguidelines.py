from __future__ import annotations

from typing import Any

from mknodes.basenodes import mkcode, mkcontainer, mktext
from mknodes.utils import log


logger = log.get_logger(__name__)


INTRO = """Link to any related issue in the Pull Request message.

During the review, we recommend using fixups:"""

SQUASH_TEXT = "Once all the changes are approved, you can squash your commits:"

OUTRO = """If this seems all too complicated, you can push or force-push each new commit,
and we will squash them ourselves if needed, before merging.
"""

FIXUP_TEXT = "git commit --fixup=SHA # SHA of commit you want to fix"
REBASE_TEXT = "git rebase -i --autosquash main"


class MkPullRequestGuidelines(mkcontainer.MkContainer):
    """Node showing pull request guidelines."""

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
            mkcode.MkCode(FIXUP_TEXT, language="bash", parent=self),
            mktext.MkText(SQUASH_TEXT, parent=self),
            mkcode.MkCode(REBASE_TEXT, language="bash", parent=self),
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

        node = MkPullRequestGuidelines()
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    guideline = MkPullRequestGuidelines()
    print(guideline)
