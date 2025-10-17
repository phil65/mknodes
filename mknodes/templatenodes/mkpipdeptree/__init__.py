from __future__ import annotations

import contextlib
import functools
import io
import types

from typing import Any, Literal

from mknodes.basenodes import mkdiagram
from mknodes.utils import helpers, log, resources


logger = log.get_logger(__name__)


@functools.cache
@helpers.list_to_tuple
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

    Args:
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
        from pipdeptree._render.mermaid import render_mermaid
        from pipdeptree._discovery import get_installed_distributions
        from pipdeptree._detect_env import detect_active_interpreter
    # dists = packagehelpers.list_pip_packages(
    #     local_only=local_only,
    #     user_only=user_only,
    #     include_editables=include_editables,
    #     editables_only=editables_only,
    # )
    # pkgs = [d._dist for d in dists]  # type: ignore[attr-defined]
    resolved_path = detect_active_interpreter()
    pkgs = get_installed_distributions(
        interpreter=resolved_path,
        local_only=local_only,
        user_only=user_only,
    )
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
            msg = f"Error when building tree for {include_list}. Is the package on PyPi?."
            logger.exception(msg)
            return ""
    tree = [tree] if isinstance(tree, str) else tree
    # Capture stdout since render_mermaid now prints instead of returning
    stdout_buffer = io.StringIO()
    with contextlib.redirect_stdout(stdout_buffer):
        render_mermaid(tree)
    text = stdout_buffer.getvalue()
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

        Args:
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
        super().__init__(direction=direction, **kwargs)

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
            self.package,
            local_only=self.local_only,
            user_only=self.user_only,
            include_editables=self.include_editables,
            editables_only=self.editables_only,
        )


if __name__ == "__main__":
    diagram = MkPipDepTree.with_context()
    print(diagram)
