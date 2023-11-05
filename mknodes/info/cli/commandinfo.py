from __future__ import annotations

import dataclasses

from mknodes.info.cli import param
from mknodes.utils import reprhelpers


@dataclasses.dataclass(frozen=True)
class CommandInfo:
    name: str
    """The name of the command."""
    description: str
    """A description for this command."""
    usage: str = ""
    """A formatted string containing a formatted "usage string" (placeholder example)"""
    subcommands: dict[str, CommandInfo] = dataclasses.field(default_factory=dict)
    """A command-name->CommandInfo mapping containing all subcommands."""
    deprecated: bool = False
    """Whether this command is deprecated."""
    epilog: str | None = None
    """Epilog for this command."""
    hidden: bool = False
    """Whether this command is hidden."""
    params: list[param.Param] = dataclasses.field(default_factory=list)
    """A list of Params for this command."""

    def __getitem__(self, name):
        return self.subcommands[name]

    def __repr__(self):
        return reprhelpers.get_dataclass_repr(self)


if __name__ == "__main__":
    from pprint import pprint

    info = CommandInfo("A", "B", "C")
    pprint(info)
