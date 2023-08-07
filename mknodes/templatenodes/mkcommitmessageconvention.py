from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mkcode, mkcontainer, mklist, mktext
from mknodes.utils import commitconventions, helpers


logger = logging.getLogger(__name__)


STYLES = {
    "Angular Style": "https://gist.github.com/stephenparish/9941e89d80e2bc58a153",
    "Karma convention": "https://karma-runner.github.io/4.0/dev/git-commit-msg.html",
}


START_TEXT = """"Commit messages must follow our convention based on {styles}:"""

COMMIT_TEXT = "<type>[(scope)]: Subject\n\n[Body]"

MID_TEXT = """**Subject and body must be valid Markdown.**
Subject must have proper casing (uppercase for first letter
if it makes sense), but no dot at the end, and no punctuation
in general.

Scope and body are optional. Type can be:

{scopes}

If you write a body, please add trailers at the end
(for example issues and PR references, or co-authors),
without relying on GitHub's flavored Markdown:
"""

BODY_TEXT = """
Body.

Issue #10: https://github.com/namespace/project/issues/10
Related to PR namespace/other-project#2: https://github.com/namespace/other-project/pull/2
"""

END_TEXT = """
These "trailers" must appear at the end of the body,
without any blank lines between them. The trailer title
can contain any character except colons `:`.
We expect a full URI for each trailer, not just GitHub autolinks
(for example, full GitHub URLs for commits and issues,
not the hash or the #issue-number).

We do not enforce a line length on commit messages summary and body,
but please avoid very long summaries, and very long lines in the body,
unless they are part of code blocks that must not be wrapped.
"""


class MkCommitMessageConvention(mkcontainer.MkContainer):
    """Text node containing Commit message conventions."""

    ICON = "simple/conventionalcommits"

    def __init__(
        self,
        scopes: list[commitconventions.ScopeStr]
        | commitconventions.ConventionTypeStr
        | None = None,
        header: str = "Commit message convention",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            scopes: Allowed commit scopes. Can be "basic", "conventional_commits"
                    or a list of scopes
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header=header, **kwargs)
        self.scopes = scopes

    def __repr__(self):
        return helpers.get_repr(self, scopes=self.scopes, _filter_empty=True)

    @property
    def items(self):
        match self.scopes:
            case "basic":
                scopes = commitconventions.basic.types
            case "convententional_commits" | "angular" | None:
                scopes = commitconventions.conventional_commits.types
            case list():
                scopes = self.scopes
            case _:
                raise TypeError(self.scopes)
        styles = " or ".join(f"[{k}]({v})" for k, v in STYLES.items())
        ls = mklist.MkList([f"`{k}`: {commitconventions.ALL_SCOPES[k]}" for k in scopes])
        return [
            mktext.MkText(START_TEXT.format(styles=styles), parent=self),
            mkcode.MkCode(COMMIT_TEXT, parent=self),
            mktext.MkText(MID_TEXT.format(scopes=ls), parent=self),
            mkcode.MkCode(BODY_TEXT, parent=self),
            mktext.MkText(END_TEXT, parent=self),
        ]

    @items.setter
    def items(self, value):
        pass

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.status = "new"  # for the small icon in the left menu
        node = MkCommitMessageConvention(header="")
        page += mknodes.MkReprRawRendered(node, indent=True, header="### All scopes")
        node = MkCommitMessageConvention(scopes=["fix", "feat", "refactor"], header="")
        page += mknodes.MkReprRawRendered(node, indent=True, header="### Selected scopes")


if __name__ == "__main__":
    conventions = MkCommitMessageConvention()
    print(conventions)
