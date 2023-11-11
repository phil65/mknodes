from __future__ import annotations

from typing import Any

from mknodes.templatenodes import mktemplate
from mknodes.utils import log
from mknodes.info.cli import clihelpers, commandinfo

logger = log.get_logger(__name__)


class MkClickDoc(mktemplate.MkTemplate):
    """Node for showing documentation for click / typer CLI apps."""

    ICON = "material/api"

    def __init__(
        self,
        target: str | None = None,
        *,
        prog_name: str | None = None,
        show_hidden: bool = False,
        show_subcommands: bool = False,
        **kwargs: Any,
    ):
        r"""Constructor.

        Arguments:
            target: Dotted path to Click command
            prog_name: Program name
            show_hidden: Show commands and options that are marked as hidden.
            show_subcommands: List subcommands of a given command.
            kwargs: Keyword arguments passed to parent
        """
        super().__init__("output/markdown/template", **kwargs)
        self.target = target
        self.prog_name = prog_name
        self.show_hidden = show_hidden
        self.show_subcommands = show_subcommands

    @property
    def info(self) -> commandinfo.CommandInfo | None:
        import importlib

        match self.target:
            case str():
                module, command = self.target.split(":")
                prog_name = self.prog_name
            case None:
                if cli_eps := self.ctx.metadata.entry_points.get("console_scripts"):
                    module, command = cli_eps[0].dotted_path.split(":")
                    prog_name = cli_eps[0].name
                return None
            case _:
                raise TypeError(self.target)
        mod = importlib.import_module(module)
        instance = getattr(mod, command)
        return clihelpers.get_cli_info(instance, command=prog_name)

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkClickDoc(target="mkdocs_mknodes.cli:cli")
        page += mk.MkReprRawRendered(node)
        node = MkClickDoc(target="mkdocs_mknodes.cli:cli", prog_name="build")
        page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    docstrings = MkClickDoc.with_context("mkdocs_mknodes.cli:cli", show_subcommands=True)
    print(docstrings)
