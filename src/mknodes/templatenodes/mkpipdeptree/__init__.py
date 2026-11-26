import functools
import types

from typing import Any, Literal

from mknodes import inputs
from mknodes.basenodes import mkdiagram
from mknodes.utils import helpers, log, resources


logger = log.get_logger(__name__)


@helpers.list_to_tuple
@functools.cache
def get_mermaid(
    package: str | tuple[str] | list[str] | None = None,
    local_only: bool = True,
    user_only: bool = False,
    reverse: bool = False,
    exclude: str = "",
) -> str:
    """Return mermaid diagram code of dependency tree.

    Mermaid graph code is returned without fences

    Args:
        package: package / packages to get a graph for. If None, include all packages
        local_only: Whether to return installs local to the current virtualenv if used
        user_only: If True, only report installation in the user
        reverse: Whether to reverse the graph
        exclude: Packages to exclude from the graph
    """
    import pipdeptree

    match package:
        case str() | None:
            packages = package
        case list() | tuple():
            packages = ",".join(package)
    try:
        text = pipdeptree.render(
            packages=packages,
            exclude=exclude or None,
            output_format="mermaid",
            reverse=reverse,
            local_only=local_only,
            user_only=user_only,
        )
    except ValueError:
        msg = f"Error when building tree for {packages}. Is the package on PyPi?."
        logger.exception(msg)
        return ""
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
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            package: Package to show a dependency diagram for
            direction: diagram direction
            local_only: Show ony local packages
            user_only: Show only user packages
            kwargs: Keyword arguments passed to parent
        """
        self._package = package
        self.local_only = local_only
        self.user_only = user_only
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

    def _tree_params(self) -> dict[str, Any]:
        return dict(package=self.package, local_only=self.local_only, user_only=self.user_only)

    def get_input_requests(self) -> list[inputs.InputRequest]:
        return [inputs.InputRequest.create("pipdeptree", **self._tree_params())]

    def get_mermaid_code(self) -> str:
        return self.ctx.inputs.get("pipdeptree", **self._tree_params())


if __name__ == "__main__":
    diagram = MkPipDepTree.with_context()
    print(diagram)
