from __future__ import annotations

from collections.abc import Callable
import dataclasses

from typing import TYPE_CHECKING, Any, Literal

from mknodes.utils import reprhelpers


if TYPE_CHECKING:
    from click import types as clicktypes


@dataclasses.dataclass(frozen=True)
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
    nargs: int | str | None = 1
    """The number of arguments this parameter matches. (Argparse may return * / ?)"""
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
    callback: Callable | None = None
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

    def __repr__(self):
        return reprhelpers.get_dataclass_repr(self)


if __name__ == "__main__":
    from pprint import pprint

    info = Param(name="test")
    pprint(info)
