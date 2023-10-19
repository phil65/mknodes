from __future__ import annotations

from typing import Any

from mknodes.basenodes import mklist
from mknodes.data import commitconventions
from mknodes.templatenodes import mkjinjatemplate
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


STYLES = {
    "Angular Style": "https://gist.github.com/stephenparish/9941e89d80e2bc58a153",
    "Karma convention": "https://karma-runner.github.io/4.0/dev/git-commit-msg.html",
}


class MkCommitConventions(mkjinjatemplate.MkJinjaTemplate):
    """Text node containing Commit message conventions."""

    ICON = "simple/conventionalcommits"
    STATUS = "new"

    def __init__(
        self,
        commit_types: (
            list[commitconventions.CommitTypeStr]
            | commitconventions.ConventionTypeStr
            | None
        ) = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            commit_types: Allowed commit commit_types. Can be "basic",
                          "conventional_commits", or a list of commit_types
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(template="commit_conventions.jinja", **kwargs)
        self._commit_types = commit_types

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            commit_types=self._commit_types,
            _filter_empty=True,
        )

    @property
    def variables(self):
        styles = " or ".join(f"[{k}]({v})" for k, v in STYLES.items())
        all_types = commitconventions.TYPE_DESCRIPTIONS
        items = [f"`{k}`: {all_types[k]}" for k in self.commit_types]
        ls = mklist.MkList(items)
        return dict(styles=styles, commit_types=str(ls))

    @variables.setter
    def variables(self, value):
        pass

    @property
    def commit_types(self) -> list[commitconventions.CommitTypeStr]:
        val: list[commitconventions.CommitTypeStr] | commitconventions.ConventionTypeStr
        match self._commit_types:
            case None:
                val = self.ctx.metadata.commit_types or "conventional_commits"
            case _:
                val = self._commit_types
        match val:
            case "basic":
                return list(commitconventions.basic.types)
            case "conventional_commits" | "angular" | None:
                return list(commitconventions.conventional_commits.types)
            case list():
                return val
            case _:
                raise TypeError(self._commit_types)

    @commit_types.setter
    def commit_types(self, value):
        self._commit_types = value

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkCommitConventions(header="")
        page += mk.MkReprRawRendered(node, header="### All commit_types")
        node = MkCommitConventions(["fix", "feat", "refactor"], header="")
        page += mk.MkReprRawRendered(node, header="### Selected commit_types")


if __name__ == "__main__":
    conventions = MkCommitConventions()
    print(conventions)
