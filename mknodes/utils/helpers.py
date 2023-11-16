from __future__ import annotations

from collections.abc import Callable, Iterable
import itertools
import os
import re

from typing import ParamSpec, TypeVar

from mknodes.utils import log


logger = log.get_logger(__name__)


T = TypeVar("T")


def slugify(text: str | os.PathLike) -> str:
    """Create a slug for given text.

    Returned text only contains alphanumerical and underscore.

    Arguments:
        text: text to get a slug for
    """
    text = str(text).lower()
    text = re.sub("[^0-9a-zA-Z_.]", "_", text)
    return re.sub("^[^0-9a-zA-Z_#]+", "", text)


def groupby(
    data: Iterable[T],
    key: Callable | str | None = None,
    *,
    sort_groups: bool = True,
    natural_sort: bool = False,
    reverse: bool = False,
) -> dict[str, list[T]]:
    """Group given iterable using given group function.

    Arguments:
        data: Iterable to group
        key: Sort function or attribute name to use for sorting
        sort_groups: Whether to sort the groups
        natural_sort: Whether to use a natural sort algorithm
        reverse: Whether to reverse the value list
    """
    if key is None:

        def keyfunc(x):
            return x

    elif isinstance(key, str):
        import operator

        keyfunc = operator.attrgetter(key)
    else:
        keyfunc = key
    if sort_groups:
        if natural_sort:
            import natsort

            data = natsort.natsorted(data, key=keyfunc)
        else:
            data = sorted(data, key=keyfunc)
    if reverse:
        data = reversed(list(data))
    return {k: list(g) for k, g in itertools.groupby(data, keyfunc)}


def groupby_first_letter(
    data: Iterable[T],
    keyfunc: Callable | None = None,
) -> dict[str, list[T]]:
    """Group given iterable by first letter.

    Arguments:
        data: Iterable to group
        keyfunc: Optional alternative sort function
    """
    data = sorted(data, key=keyfunc or (lambda x: x))

    def first_letter(x):
        return keyfunc(x)[0] if keyfunc else x[0]

    return {k: list(g) for k, g in itertools.groupby(data, first_letter)}


def label_for_class(klass: type) -> str:
    mod = klass.__module__
    parts = mod.split(".")
    if mod.startswith("prettyqt."):
        return f"{parts[1]}.{klass.__name__}"
    return f"{parts[-1]}.{klass.__name__}"


T = TypeVar("T")


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
    strings = groupby_first_letter([str(i) for i in range(1000)])
    print(strings)
