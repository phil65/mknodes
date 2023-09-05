from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import reprhelpers


logger = logging.getLogger(__name__)


class MkClickDoc(mknode.MkNode):
    """Documentation for click CLI apps."""

    REQUIRED_EXTENSIONS = ["mkdocs-click"]
    ICON = "material/api"

    def __init__(
        self,
        target: str | None = None,
        prog_name: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            target: Dotted path to Click group
            prog_name: Program name
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self._target = target
        self._prog_name = prog_name

    def __repr__(self):
        return reprhelpers.get_repr(self, target=self._target)

    @property
    def attributes(self) -> dict[str, str | None]:
        match self._target:
            case str():
                module, command = self._target.split(":")
                return dict(module=module, command=command, prog_name=self._prog_name)
            case None if self.associated_project:
                info = self.associated_project.info
                eps = info.get_entry_points("console_scripts")
                if eps:
                    ep = next(iter(eps.values()))
                    module, command = ep.dotted_path.split(":")
                    return dict(module=module, command=command, prog_name=ep.name)
        return {}

    def _to_markdown(self) -> str:
        if not self.attributes:
            return ""
        md = "::: mkdocs-click"
        option_lines = [f"    :{k}: {v}" for k, v in self.attributes.items() if v]
        option_text = "\n".join(option_lines)
        return f"{md}\n{option_text}\n"

    @staticmethod
    def create_example_page(page):
        # import mknodes

        page += "The MkClickDoc node shows DocStrings from mkdocstrings addon."
        page += MkClickDoc(target="mknodes.cli:cli")
        # node = MkClickDoc(module="cli", command="cli")
        # page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    docstrings = MkClickDoc(target="mknodes.cli:cli")
    print(docstrings)
