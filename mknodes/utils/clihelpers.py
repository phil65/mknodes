from __future__ import annotations

import dataclasses

from typing import Any

import click
import typer

from typer.main import get_command

from mknodes.basenodes import mkcode


@dataclasses.dataclass
class Param:
    count: bool = False
    default: Any = None
    envvar: str | None = None
    flag_value: bool = False
    help: str | None = None  # noqa: A003
    hidden: bool = False
    is_flag: bool = False
    multiple: bool = False
    name: str = ""
    nargs: int = 1
    opts: list[str] = dataclasses.field(default_factory=list)
    param_type_name: str = "option"
    prompt: Any = None
    required: bool = False
    secondary_opts: list[str] = dataclasses.field(default_factory=list)
    type: dict[str, str] = dataclasses.field(default_factory=dict)  # noqa: A003

    def to_markdown(self):
        opt_str = ", ".join(f"`{i}`" for i in reversed(self.opts))
        lines = [f"### {opt_str}"]
        if self.required:
            lines.append("**REQUIRED**")
        if self.envvar:
            lines.append(f"**Environment variable:** {self.envvar}")
        if self.multiple:
            lines.append("**Multiple values allowed.**")
        if self.default:
            lines.append(f"**Default:** {self.default}")
        if self.is_flag:
            lines.append(f"**Flag:** {self.flag_value}")
        if self.help:
            lines.append(self.help)
        return "\n\n".join(lines)


@dataclasses.dataclass
class CommandInfo:
    name: str
    description: str
    usage: str
    subcommands: dict[str, CommandInfo] = dataclasses.field(default_factory=dict)
    deprecated: bool = False
    epilog: str | None = None
    hidden: bool = False
    params: list[Param] = dataclasses.field(default_factory=list)

    def __getitem__(self, name):
        return self.subcommands[name]

    def to_markdown(self, recursive: bool = False):
        header = f"## {self.name}\n\n"
        text = header + self.description + "\n\n" + str(mkcode.MkCode(self.usage))
        params = [i.to_markdown() for i in self.params]
        cmd_text = text + "\n\n\n" + "\n\n\n".join(params)
        if not recursive:
            return cmd_text
        children_text = "\n".join(
            i.to_markdown(recursive=True) for i in self.subcommands.values()
        )
        return cmd_text + children_text


def get_typer_info(
    instance: typer.Typer | click.Group,
    command: str | None = None,
) -> CommandInfo:
    cmd = get_command(instance) if isinstance(instance, typer.Typer) else instance
    info = get_command_info(cmd)
    if command:
        ctx = typer.Context(cmd)
        subcommands = getattr(cmd, "commands", {})
        cmds = {k: get_command_info(v, parent=ctx) for k, v in subcommands.items()}
        return cmds.get(command, info)
    return info


def get_command_info(command: click.Command, parent=None) -> CommandInfo:
    ctx = typer.Context(command, parent=parent)
    subcommands = getattr(command, "commands", {})
    dct = ctx.command.to_info_dict(ctx)
    return CommandInfo(
        name=ctx.command.name or "",
        description=ctx.command.help or ctx.command.short_help or "",
        usage=_make_usage(ctx),
        params=[Param(**i) for i in dct["params"]],
        subcommands={k: get_command_info(v, parent=ctx) for k, v in subcommands.items()},
        deprecated=dct["deprecated"],
        epilog=dct["epilog"],
        hidden=dct["hidden"],
    )


def _make_usage(ctx: click.Context) -> str:
    """Create the Markdown lines from the command usage string."""
    # Gets the usual 'Usage' string without the prefix.
    formatter = ctx.make_formatter()
    pieces = ctx.command.collect_usage_pieces(ctx)
    formatter.write_usage(ctx.command_path, " ".join(pieces), prefix="")
    usage = formatter.getvalue().rstrip("\n")
    # Generate the full usage string based on parents if any, i.e. `root sub1 sub2 ...`.
    full_path = []
    current: click.Context | None = ctx
    while current is not None:
        name = current.command.name.lower() if current.command.name else ""
        full_path.append(name)
        current = current.parent

    full_path.reverse()
    return " ".join(full_path) + usage


if __name__ == "__main__":
    from pprint import pprint

    import mkdocs.__main__

    info = get_typer_info(mkdocs.__main__.cli, command="mkdocs")
    pprint(info.to_markdown(recursive=True))
