from __future__ import annotations

import dataclasses

import click
import typer

from typer.main import get_command


@dataclasses.dataclass
class CommandInfo:
    title: str
    description: str
    usage: str
    options: str
    subcommands: dict[str, CommandInfo] = dataclasses.field(default_factory=dict)

    def __getitem__(self, name):
        return self.subcommands[name]


def get_typer_info(typer_instance: typer.Typer) -> CommandInfo:
    cmd = get_command(typer_instance)
    return get_command_info(cmd)


def get_command_info(command: click.Command, parent=None) -> CommandInfo:
    ctx = typer.Context(command, parent=parent)
    subcommands = getattr(command, "commands", {})
    formatter = ctx.make_formatter()
    click.Command.format_options(ctx.command, ctx, formatter)
    return CommandInfo(
        title=ctx.command.name or "",
        description=ctx.command.help or ctx.command.short_help or "",
        usage=_make_usage(ctx),
        options=formatter.getvalue(),
        # ctx.command_path
        subcommands={k: get_command_info(v, parent=ctx) for k, v in subcommands.items()},
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
        name = current.command.name
        if name is None:
            msg = f"command {current.command} has no `name`"
            raise RuntimeError(msg)
        full_path.append(name)
        current = current.parent

    full_path.reverse()
    return " ".join(full_path) + usage


if __name__ == "__main__":
    from pprint import pprint

    from mknodes import cli

    info = get_typer_info(cli.cli)
    pprint(info)
