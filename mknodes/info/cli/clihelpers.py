from __future__ import annotations

import argparse

from typing import TYPE_CHECKING

from mknodes.info.cli import commandinfo, param


if TYPE_CHECKING:
    import click
    import typer


def get_argparse_info(parser: argparse.ArgumentParser):
    subcommands = [
        commandinfo.CommandInfo(name=i.title or "", description=i.description or "")
        for i in parser._action_groups
    ]
    params = [
        param.Param(
            metavar=" ".join(i.metavar) if isinstance(i.metavar, tuple) else i.metavar,
            help=i.help,
            default=i.default if i.default != argparse.SUPPRESS else None,
            opts=list(i.option_strings),
            nargs=i.nargs,
            required=i.required,
            # dest: str
            # const: Any
            # choices: Iterable[Any] | None
        )
        for i in parser._actions
    ]
    return commandinfo.CommandInfo(
        name=parser.prog,
        description=parser.description or "",
        usage=parser.format_usage(),
        params=params,
        subcommands={i.name: i for i in subcommands},
    )


def get_cli_info(
    instance: typer.Typer | click.Group | argparse.ArgumentParser,
    command: str | None = None,
) -> commandinfo.CommandInfo:
    """Return a `CommmandInfo` object for command of given instance.

    Instance can either be a click Group, a Typer instance or an ArgumentParser

    Arguments:
        instance: A `Typer`, **click** `Group` or `ArgumentParser` instance
        command: The command to get info for.
    """
    if isinstance(instance, argparse.ArgumentParser):
        info = get_argparse_info(instance)
        return info[command] if command else info

    import typer

    from typer.main import get_command

    cmd = get_command(instance) if isinstance(instance, typer.Typer) else instance
    info = get_click_info(cmd)
    if command:
        ctx = typer.Context(cmd)
        subcommands = getattr(cmd, "commands", {})
        cmds = {k: get_click_info(v, parent=ctx) for k, v in subcommands.items()}
        return cmds.get(command, info)
    return info


def get_click_info(
    command: click.Command,
    parent: click.Context | None = None,
) -> commandinfo.CommandInfo:
    """Get a `CommandInfo` dataclass for given click `Command`.

    Arguments:
        command: The **click** `Command` to get info for.
        parent: The optional parent context
    """
    import click

    ctx = click.Context(command, parent=parent)
    subcommands = getattr(command, "commands", {})
    dct = ctx.command.to_info_dict(ctx)
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
    return commandinfo.CommandInfo(
        name=ctx.command.name or "",
        description=ctx.command.help or ctx.command.short_help or "",
        usage=" ".join(full_path) + usage,
        params=[param.Param(**i) for i in dct["params"]],
        subcommands={k: get_click_info(v, parent=ctx) for k, v in subcommands.items()},
        deprecated=dct["deprecated"],
        epilog=dct["epilog"],
        hidden=dct["hidden"],
    )


if __name__ == "__main__":
    from pprint import pprint

    import mkdocs.__main__

    info = get_cli_info(mkdocs.__main__.cli, command="mkdocs")
    pprint(info)
