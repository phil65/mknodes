from __future__ import annotations

import itertools
import textwrap

from typing import Any, Literal

from jinjarope import iterfilters, utils
from pymdownx import superfences

from mknodes.basenodes import mkcode
from mknodes.utils import resources


GraphTypeStr = Literal["flow", "sequence", "state"]

config = {
    "custom_fences": [
        {"name": "mermaid", "class": "mermaid", "format": superfences.fence_code_format},
    ],
}


class MkDiagram(mkcode.MkCode):
    """Class representing a mermaid diagram.

    MkDiagrams can show directed acyclic graphs and allows to manually
    create diagrams.
    """

    ICON = "material/graph-outline"
    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.superfences", **config)]

    def __init__(
        self,
        names: list[str] | None = None,
        connections: list[tuple] | None = None,
        *,
        direction: Literal["TD", "DT", "LR", "RL"] = "TD",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            names: names which should be part of the diagram
            connections: tuples indicating the connections of the names
            direction: diagram direction
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(language="mermaid", **kwargs)
        self.direction = direction
        # Preserve order. Useful if only names are passed, order is important then.
        self.names = iterfilters.reduce_list(names or [])
        self.connections = set(connections or [])

    @property
    def text(self) -> str:
        """MkCode override."""
        return f"graph {self.direction}\n{self.mermaid_code}"

    @property
    def mermaid_code(self) -> str:
        """Return code block, excluding fences and (graph type direction) line.

        Can be overriden by subclasses.
        """
        lines = list(self.names)
        if not self.connections:
            lines = [f'{utils.get_hash(i)}["{i}"]' for i in lines]
            for prev, nxt in itertools.pairwise(self.names):
                lines.append(f"{utils.get_hash(prev)} --> {utils.get_hash(nxt)}")
            return textwrap.indent("\n".join(lines), "  ")
        for connection in self.connections:
            if len(connection) == 2:  # noqa: PLR2004
                source, target = connection
                lines.append(f"{source} --> {target}")
            elif len(connection) == 3:  # noqa: PLR2004
                source, target, mark = connection
                lines.append(f"{source} --> |{mark}| {target}")
            else:
                msg = f"Tuple with wrong length: {connection}"
                raise TypeError(msg)
        return textwrap.indent("\n".join(lines), "  ")

    @property
    def fence_title(self) -> str:
        """MkCode override."""
        return "mermaid"


if __name__ == "__main__":
    diagram = MkDiagram(["a", "b", "c", "d"])
    print(diagram)
