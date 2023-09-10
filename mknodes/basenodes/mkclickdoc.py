from __future__ import annotations

from typing import Any, Literal

from mknodes.basenodes import mknode
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


class MkClickDoc(mknode.MkNode):
    """Documentation for click / typer CLI apps."""

    REQUIRED_EXTENSIONS = ["mkdocs-typer", "attr_list"]
    ICON = "material/api"

    def __init__(
        self,
        target: str | None = None,
        prog_name: str | None = None,
        depth: int | None = None,
        style: Literal["plain", "table"] | None = None,
        remove_ascii_art: bool = False,
        show_hidden: bool = False,
        show_subcommands: bool = False,
        **kwargs: Any,
    ):
        r"""Constructor.

        Arguments:
            target: Dotted path to Click command
            prog_name: Program name
            depth: Offset to add when generating headers.
            style: Style for the options section.
            remove_ascii_art: When docstrings begin with the escape character \b, all
                              text will be ignored until next blank line is encountered.
            show_hidden: Show commands and options that are marked as hidden.
            show_subcommands: List subcommands of a given command.
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self._target = target
        self._prog_name = prog_name
        self._depth = depth
        self.style = style
        self.remove_ascii_art = remove_ascii_art
        self.show_hidden = show_hidden
        self.show_subcommands = show_subcommands

    def __repr__(self):
        return reprhelpers.get_repr(self, target=self._target)

    @property
    def attributes(self) -> dict[str, str | None]:
        # sourcery skip: use-named-expression
        dct: dict[str, Any] = {}
        match self._target:
            case str():
                module, command = self._target.split(":")
                dct = dict(module=module, command=command, prog_name=self._prog_name)
            case None:
                eps = self.ctx.metadata.entry_points
                eps = [i for i in eps.values() if i.group == "console_scripts"]
                if eps:
                    module, command = eps[0].dotted_path.split(":")
                    dct = dict(module=module, command=command, prog_name=eps[0].name)
        if not dct:
            return {}
        dct.update(
            depth=self._depth,
            style=self.style,
            remove_ascii_art=self.remove_ascii_art,
            show_hidden=self.show_hidden,
            show_subcommands=self.show_subcommands,
        )
        return dct

    def _to_markdown(self) -> str:
        if not self.attributes:
            return ""
        app = self.ctx.metadata.cli
        if not app:
            return ""
        md = f"::: mkdocs-{app}"
        option_lines = [f"    :{k}: {v}" for k, v in self.attributes.items() if v]
        option_text = "\n".join(option_lines)
        return f"{md}\n{option_text}\n\n"

    @staticmethod
    def create_example_page(page):
        # import mknodes

        page += "The MkClickDoc node shows DocStrings for Click / Typer."
        page += MkClickDoc(target="mknodes.cli:cli")
        # node = MkClickDoc(module="cli", command="cli")
        # page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    docstrings = MkClickDoc.with_default_context()
    print(docstrings)
