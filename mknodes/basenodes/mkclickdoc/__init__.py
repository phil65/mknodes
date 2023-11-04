from __future__ import annotations

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import clihelpers, log


logger = log.get_logger(__name__)


class MkClickDoc(mknode.MkNode):
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
        super().__init__(**kwargs)
        self.target = target
        self.prog_name = prog_name
        self.show_hidden = show_hidden
        self.show_subcommands = show_subcommands

    @property
    def attributes(self) -> dict[str, Any]:
        # sourcery skip: use-named-expression
        dct: dict[str, Any] = {}
        match self.target:
            case str():
                module, command = self.target.split(":")
                dct = dict(module=module, command=command, prog_name=self.prog_name)
            case None:
                if cli_eps := self.ctx.metadata.entry_points.get("console_scripts"):
                    module, command = cli_eps[0].dotted_path.split(":")
                    dct = dict(module=module, command=command, prog_name=cli_eps[0].name)
        if not dct:
            return {}
        dct.update(show_hidden=self.show_hidden, show_subcommands=self.show_subcommands)
        return dct

    def _to_markdown(self) -> str:
        import importlib

        if not self.attributes:
            return ""
        attrs = self.attributes
        mod = importlib.import_module(attrs["module"])
        instance = getattr(mod, attrs["command"])

        def param_to_md(param) -> str:
            lines = [f"### {param.opt_str}"]
            if param.required:
                lines.append("**REQUIRED**")
            if param.envvar:
                lines.append(f"**Environment variable:** {param.envvar}")
            if param.multiple:
                lines.append("**Multiple values allowed.**")
            if param.default:
                lines.append(f"**Default:** {param.default}")
            if param.is_flag:
                lines.append(f"**Flag:** {param.flag_value}")
            if param.help:
                lines.append(param.help)
            return "\n\n".join(lines)

        def info_to_md(info, recursive: bool = False) -> str:
            import mknodes as mk

            header = f"## {info.name}\n\n"
            text = header + info.description + "\n\n" + str(mk.MkCode(info.usage))
            params = [param_to_md(i) for i in info.params]
            cmd_text = text + "\n\n\n" + "\n\n\n".join(params)
            if not recursive:
                return cmd_text
            children_text = "\n".join(
                info_to_md(i, recursive=True) for i in info.subcommands.values()
            )
            return cmd_text + children_text

        info = clihelpers.get_typer_info(instance, command=attrs["prog_name"])
        return info_to_md(info, recursive=self.show_subcommands)

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkClickDoc(target="mkdocs_mknodes.cli:cli")
        page += mk.MkReprRawRendered(node)
        node = MkClickDoc(target="mkdocs_mknodes.cli:cli", prog_name="build")
        page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    docstrings = MkClickDoc.with_context("mkdocs_mknodes.cli:cli")
    print(docstrings)
