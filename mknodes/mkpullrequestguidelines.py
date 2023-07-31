from __future__ import annotations

import logging

from mknodes import mknode


logger = logging.getLogger(__name__)


TEXT = """Link to any related issue in the Pull Request message.

During the review, we recommend using fixups:

```bash
# SHA is the SHA of the commit you want to fix
git commit --fixup=SHA
```

Once all the changes are approved, you can squash your commits:

```bash
git rebase -i --autosquash main
```

And force-push:

```bash
git push -f
```

If this seems all too complicated, you can push or force-push each new commit,
and we will squash them ourselves if needed, before merging.
"""


class MkPullRequestGuidelines(mknode.MkNode):
    """Pull request guide text."""

    def __init__(
        self,
        header: str = "Pull request guidelines",
        **kwargs,
    ):
        super().__init__(header=header, **kwargs)

    def _to_markdown(self) -> str:
        return TEXT

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkPullRequestGuidelines()
        page += node
        page += mknodes.MkHtmlBlock(str(node), header="Markdown")


if __name__ == "__main__":
    guideline = MkPullRequestGuidelines()
    print(guideline)
