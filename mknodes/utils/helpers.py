from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from mknodes.utils import log


if TYPE_CHECKING:
    from collections.abc import Callable, Iterable


logger = log.get_logger(__name__)


T = TypeVar("T")


def label_for_class(klass: type) -> str:
    mod = klass.__module__
    parts = mod.split(".")
    if mod.startswith("prettyqt."):
        return f"{parts[1]}.{klass.__name__}"
    return f"{parts[-1]}.{klass.__name__}"


def get_indented_lines(lines: Iterable[str], indent: int | str = 4) -> list[str]:
    """Return all lines until a line is not indented with given indent.

    Returned lines are unindented.

    Arguments:
        lines: Lines to check for indented lines
        indent: Indentation to check
    """
    indent_str = indent if isinstance(indent, str) else " " * indent
    if indented := list(itertools.takewhile(lambda x: x.startswith(indent_str), lines)):
        return [j[len(indent_str) :] for j in indented]
    return []


def is_url(string: str) -> bool:
    """Return true when given string represents a HTTP url.

    Arguments:
        string: The string to check
    """
    return string.startswith(("http:/", "https:/", "www."))


P = ParamSpec("P")
R = TypeVar("R")


def list_to_tuple(fn: Callable[P, R]) -> Callable[P, R]:
    """Decorator to convert lists to tuples in the arguments.

    Arguments:
        fn: The function to decorate
    """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        safe_args = [tuple(item) if isinstance(item, list) else item for item in args]
        if kwargs:
            kwargs = {
                key: tuple(value) if isinstance(value, list) else value
                for key, value in kwargs.items()
            }  # type: ignore[assignment]
        return fn(*safe_args, **kwargs)  # type: ignore[arg-type]

    return wrapper


if __name__ == "__main__":
    is_url("abc")
