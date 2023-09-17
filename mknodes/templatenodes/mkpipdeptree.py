from __future__ import annotations

import functools
import types

from typing import Any, Literal

from mknodes import project
from mknodes.basenodes import mkdiagram
from mknodes.utils import reprhelpers


@functools.cache
def get_mermaid(
    package: str | list[str] | None = None,
    local_only: bool = False,
    user_only: bool = False,
    reverse: bool = False,
    exclude: str = "",
) -> str:
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        from pipdeptree._discovery import get_installed_distributions
        from pipdeptree._models import PackageDAG
        from pipdeptree._render import render_mermaid

    pkgs = get_installed_distributions(local_only=local_only, user_only=user_only)
    tree = PackageDAG.from_pkgs(pkgs)
    # Reverse the tree (if applicable) before filtering,
    # thus ensuring, that the filter will be applied on ReverseTree
    if reverse:
        tree = tree.reverse()
    show_only = package.split(",") if isinstance(package, str) else package
    exclude_list = set(exclude.split(",")) if exclude else None
    if show_only is not None or exclude_list is not None:
        tree = tree.filter_nodes(show_only, exclude_list)
    tree = [tree] if isinstance(tree, str) else tree
    text = render_mermaid(tree)
    return "\n".join(text.splitlines()[1:])


class MkPipDepTree(mkdiagram.MkDiagram):
    """Node to display a mermaid diagram for the dependencies."""

    def __init__(
        self,
        package: types.ModuleType | str | None = None,
        direction: Literal["TD", "DT", "LR", "RL"] = "TD",
        local_only: bool = False,
        user_only: bool = False,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            package: Package to show a dependency diagram for
            direction: diagram direction
            local_only: Show ony local packages
            user_only: Show only user packages
            kwargs: Keyword arguments passed to parent
        """
        self._package = package
        self.local_only = local_only
        self.user_only = user_only
        super().__init__(graph_type="flow", direction=direction, **kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            package=self._package,
            local_only=self.local_only,
            user_only=self.user_only,
            direction=self.direction,
            _filter_empty=True,
            _filter_false=True,
        )

    @staticmethod
    def create_example_page(page):
        import mknodes

        tree = MkPipDepTree(direction="LR")
        page += mknodes.MkReprRawRendered(tree)
        tree = MkPipDepTree("mkdocstrings", direction="LR")
        page += mknodes.MkReprRawRendered(tree)

    @property
    def package(self):
        match self._package:
            case None:
                return self.ctx.metadata.distribution_name
            case types.ModuleType():
                return self._package.__name__
            case _:
                return self._package

    @property
    def mermaid_code(self) -> str:
        return get_mermaid(
            self.package,
            local_only=self.local_only,
            user_only=self.user_only,
        )


if __name__ == "__main__":
    proj = project.Project.for_mknodes()
    diagram = MkPipDepTree(project=proj)
    print(diagram)
