from __future__ import annotations

from typing import Any

from mknodes.templatenodes import mktemplate


class MkPullRequestGuidelines(mktemplate.MkTemplate):
    """Node showing pull request guidelines."""

    ICON = "octicons/git-pull-request-24"

    def __init__(self, **kwargs: Any):
        """Constructor.

        Arguments:
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(template="pullrequest_guidelines.jinja", **kwargs)


if __name__ == "__main__":
    guideline = MkPullRequestGuidelines()
    print(guideline)
