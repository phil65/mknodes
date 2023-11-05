from __future__ import annotations

import functools
import types

from typing import Any, Literal

from mknodes.basenodes import mkdiagram
from mknodes.utils import log, packagehelpers, resources


logger = log.get_logger(__name__)


@functools.cache
def get_mermaid(
    package: str | tuple[str] | None = None,
    local_only: bool = True,
    user_only: bool = False,
    include_editables: bool = True,
    editables_only: bool = False,
    reverse: bool = False,
    exclude: str = "",
) -> str:
    """Return mermaid diagram code of dependency tree.

    Mermaid graph code is returned without fences

    Arguments:
        package: package / packages to get a graph for. If None, include all packages
        local_only: Whether to return installs local to the current virtualenv if used
        user_only: If True, only report installation in the user
        include_editables: Whether to include editable installs
        editables_only: Only return editable installs
        reverse: Whether to reverse the graph
        exclude: Packages to exclude from the graph
    """
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        from pipdeptree._models import PackageDAG
        from pipdeptree._render import render_mermaid

    dists = packagehelpers.list_pip_packages(
        local_only=local_only,
        user_only=user_only,
        include_editables=include_editables,
        editables_only=editables_only,
    )
    pkgs = [d._dist for d in dists]  # type: ignore[attr-defined]
    tree = PackageDAG.from_pkgs(pkgs)
    # Reverse the tree (if applicable) before filtering,
    # thus ensuring, that the filter will be applied on ReverseTree
    if reverse:
        tree = tree.reverse()
    match package:
        case str():
            include_list = package.split(",")
        case list() | tuple():
            include_list = list(package)
        case None:
            include_list = None
    exclude_list = set(exclude.split(",")) if exclude else None
    if include_list is not None or exclude_list is not None:
        try:
            tree = tree.filter_nodes(include_list, exclude_list)
        except ValueError:
            msg = "Error when filtering nodes for pipdeptree. Is the package on PyPi?."
            logger.exception(msg)
            return ""
    tree = [tree] if isinstance(tree, str) else tree
    text = render_mermaid(tree)
    return "\n".join(text.splitlines()[1:])


class MkPipDepTree(mkdiagram.MkDiagram):
    """Node to display a mermaid diagram for the dependencies."""

    REQUIRED_PACKAGES = [resources.Package("pipdeptree")]
    ICON = "material/dependency"

    def __init__(
        self,
        package: types.ModuleType | str | None = None,
        *,
        direction: Literal["TD", "DT", "LR", "RL"] = "TD",
        local_only: bool = False,
        user_only: bool = False,
        include_editables: bool = True,
        editables_only: bool = False,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            package: Package to show a dependency diagram for
            direction: diagram direction
            local_only: Show ony local packages
            user_only: Show only user packages
            include_editables: Whether to include editable installs
            editables_only: Only return editable installs
            kwargs: Keyword arguments passed to parent
        """
        self._package = package
        self.local_only = local_only
        self.user_only = user_only
        self.include_editables = include_editables
        self.editables_only = editables_only
        super().__init__(graph_type="flow", direction=direction, **kwargs)

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        tree = MkPipDepTree(direction="LR")
        page += mk.MkReprRawRendered(tree)
        tree = MkPipDepTree("mkdocstrings", direction="LR")
        page += mk.MkReprRawRendered(tree)

    @property
    def package(self) -> str:
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
            tuple(self.package) if isinstance(self.package, list) else self.package,
            local_only=self.local_only,
            user_only=self.user_only,
            include_editables=self.include_editables,
            editables_only=self.editables_only,
        )


if __name__ == "__main__":
    diagram = MkPipDepTree.with_context()
    print(diagram)
