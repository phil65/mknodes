from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mkcode, mkcontainer, mklist, mktext
from mknodes.data import commitconventions
from mknodes.utils import helpers


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

{commit_types}

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


class MkCommitConventions(mkcontainer.MkContainer):
    """Text node containing Commit message conventions."""

    ICON = "simple/conventionalcommits"
    STATUS = "new"

    def __init__(
        self,
        commit_types: list[commitconventions.CommitTypeStr]
        | commitconventions.ConventionTypeStr
        | None = None,
        header: str = "Commit message convention",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            commit_types: Allowed commit commit_types. Can be "basic",
                          "conventional_commits", or a list of commit_types
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header=header, **kwargs)
        self.commit_types = commit_types

    def __repr__(self):
        return helpers.get_repr(self, commit_types=self.commit_types, _filter_empty=True)

    @property
    def items(self):
        match self.commit_types:
            case None if self.associated_project:
                val = self.associated_project.commit_types
            case None:
                val = "conventional_commits"
            case _:
                val = self.commit_types
        match val:
            case "basic":
                commit_types = commitconventions.basic.types
            case "conventional_commits" | "angular" | None:
                commit_types = commitconventions.conventional_commits.types
            case list():
                commit_types = val
            case _:
                raise TypeError(self.commit_types)
        styles = " or ".join(f"[{k}]({v})" for k, v in STYLES.items())
        all_types = commitconventions.ALL_COMMIT_TYPES
        ls = mklist.MkList([f"`{k}`: {all_types[k]}" for k in commit_types])
        return [
            mktext.MkText(START_TEXT.format(styles=styles), parent=self),
            mkcode.MkCode(COMMIT_TEXT, language="md", parent=self),
            mktext.MkText(MID_TEXT.format(commit_types=ls), parent=self),
            mkcode.MkCode(BODY_TEXT, language="md", parent=self),
            mktext.MkText(END_TEXT, parent=self),
        ]

    @items.setter
    def items(self, value):
        pass

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkCommitConventions(header="")
        page += mknodes.MkReprRawRendered(node, header="### All commit_types")
        node = MkCommitConventions(
            commit_types=["fix", "feat", "refactor"],
            header="",
        )
        page += mknodes.MkReprRawRendered(node, header="### Selected commit_types")


if __name__ == "__main__":
    conventions = MkCommitConventions()
    print(conventions)