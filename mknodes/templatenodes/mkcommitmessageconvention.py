from __future__ import annotations

import logging

from typing import Any, Literal

from mknodes.basenodes import mklist, mknode
from mknodes.utils import helpers


logger = logging.getLogger(__name__)

ScopeStr = Literal[
    "build",
    "chore",
    "ci",
    "deps",
    "docs",
    "feat",
    "fix",
    "perf",
    "refactor",
    "style",
    "tests",
]

SCOPES: dict[ScopeStr, str] = {
    "build": "About packaging, building wheels, etc.",
    "chore": "About packaging or repo/files management.",
    "ci": "About Continuous Integration.",
    "deps": "Dependencies update.",
    "docs": "About documentation.",
    "feat": "New feature.",
    "fix": "Bug fix.",
    "perf": "About performance.",
    "refactor": "Changes that are not features or bug fixes.",
    "style": "A change in code style/format.",
    "tests": "About tests.",
}

STYLES = {
    "Angular Style": "https://gist.github.com/stephenparish/9941e89d80e2bc58a153",
    "Karma convention": "https://karma-runner.github.io/4.0/dev/git-commit-msg.html",
}

TEXT = """Commit messages must follow our convention based on {styles}:

```
<type>[(scope)]: Subject

[Body]
```

**Subject and body must be valid Markdown.**
Subject must have proper casing (uppercase for first letter
if it makes sense), but no dot at the end, and no punctuation
in general.

Scope and body are optional. Type can be:

{scopes}

If you write a body, please add trailers at the end
(for example issues and PR references, or co-authors),
without relying on GitHub's flavored Markdown:

```
Body.

Issue #10: https://github.com/namespace/project/issues/10
Related to PR namespace/other-project#2: https://github.com/namespace/other-project/pull/2
```

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


class MkCommitMessageConvention(mknode.MkNode):
    """Text node containing Commit message conventions."""

    ICON = "simple/conventionalcommits"

    def __init__(
        self,
        scopes: list[ScopeStr] | None = None,
        header: str = "Commit message convention",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            scopes: Allowed commit scopes
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header=header, **kwargs)
        self.scopes = scopes

    def __repr__(self):
        return helpers.get_repr(self, scopes=self.scopes, _filter_empty=True)

    def _to_markdown(self) -> str:
        styles = " or ".join(f"[{k}]({v})" for k, v in STYLES.items())
        scopes = self.scopes or list(SCOPES.keys())
        scope_str = mklist.MkList([f"`{k}`: {SCOPES[k]}" for k in scopes])
        return TEXT.format(styles=styles, scopes=scope_str)

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.status = "new"  # for the small icon in the left menu
        node = MkCommitMessageConvention()
        page += mknodes.MkReprRawRendered(node, indent=True)


if __name__ == "__main__":
    conventions = MkCommitMessageConvention()
    print(conventions)
