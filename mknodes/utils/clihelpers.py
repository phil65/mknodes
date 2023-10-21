from __future__ import annotations

from collections.abc import Callable
import dataclasses

from typing import TYPE_CHECKING, Any, Literal


if TYPE_CHECKING:
    import click

    from click import types as clicktypes
    import typer


@dataclasses.dataclass
class Param:
    count: bool = False
    """Whether the parameter increments an integer."""
    default: Any = None
    """The default value of the parameter."""
    envvar: str | None = None
    """ the environment variable name for this parameter."""
    flag_value: bool = False
    """ Value used for this flag if enabled."""
    help: str | None = None  # noqa: A003
    """A formatted help text for this parameter."""
    hidden: bool = False
    """Whether this parameter is hidden."""
    is_flag: bool = False
    """Whether the parameter is a flag."""
    multiple: bool = False
    """Whether the parameter is accepted multiple times and recorded."""
    name: str = ""
    """The name of this parameter."""
    nargs: int = 1
    """The number of arguments this parameter matches."""
    opts: list[str] = dataclasses.field(default_factory=list)
    """Options for this parameter."""
    param_type_name: Literal["option", "parameter", "argument"] = "option"
    """The type of the parameter."""
    prompt: Any = None
    """Whether user is prompted for this parameter."""
    required: bool = False
    """Whether the parameter is required."""
    secondary_opts: list[str] = dataclasses.field(default_factory=list)
    """Secondary options for this parameter."""
    type: clicktypes.ParamType | None = None  # noqa: A003
    """The type object of the parameter."""
    callback: Callable[[click.Context, click.Parameter, Any], Any] | None = None
    """A method to further process the value after type conversion."""
    expose_value: str = ""
    """Whether value is passed onwards to the command callback and stored in context."""
    is_eager: bool = False
    """Whether the param is eager."""
    metavar: str | None = None
    """How value is represented in the help page."""

    @property
    def opt_str(self) -> str:
        """A formatted and sorted string containing the the options."""
        return ", ".join(f"`{i}`" for i in reversed(self.opts))

    def to_markdown(self):
        lines = [f"### {self.opt_str}"]
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
    """The name of the command."""
    description: str
    """A description for this command."""
    usage: str
    """A formatted string containing a formatted "usage string" (placeholder example)"""
    subcommands: dict[str, CommandInfo] = dataclasses.field(default_factory=dict)
    """A command-name->CommandInfo mapping containing all subcommands."""
    deprecated: bool = False
    """Whether this command is deprecated."""
    epilog: str | None = None
    """Epilog for this command."""
    hidden: bool = False
    """Whether this command is hidden."""
    params: list[Param] = dataclasses.field(default_factory=list)
    """A list of Params for this command."""

    def __getitem__(self, name):
        return self.subcommands[name]

    def to_markdown(self, recursive: bool = False):
        import mknodes as mk

        header = f"## {self.name}\n\n"
        text = header + self.description + "\n\n" + str(mk.MkCode(self.usage))
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
    """Return a `CommmandInfo` object for command of given `Typer` instance.

    Arguments:
        instance: A `Typer` or **click** `Group` instance
        command: The command to get info for.
    """
    import typer

    from typer.main import get_command

    cmd = get_command(instance) if isinstance(instance, typer.Typer) else instance
    info = get_command_info(cmd)
    if command:
        ctx = typer.Context(cmd)
        subcommands = getattr(cmd, "commands", {})
        cmds = {k: get_command_info(v, parent=ctx) for k, v in subcommands.items()}
        return cmds.get(command, info)
    return info


def get_command_info(
    command: click.Command,
    parent: click.Context | None = None,
) -> CommandInfo:
    """Get a `CommandInfo` dataclass for given click `Command`.

    Arguments:
        command: The **click** `Command` to get info for.
        parent: The optional parent context
    """
    import typer

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
    """Create the full command usage string.

    Arguments:
        ctx: The context to create a usage string for.
    """
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
