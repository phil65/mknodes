from __future__ import annotations

import contextlib
import functools
import inspect
import itertools
import pathlib
import types

from mknodes.data import datatypes
from mknodes.utils import helpers, log


RESPONSE_CODE_OK = 200

logger = log.get_logger(__name__)


@functools.cache
def get_function_body(func: types.MethodType | types.FunctionType | type) -> str:
    """Get body of given function. Strips off the signature.

    Arguments:
        func: Callable to get the body from
    """
    # see https://stackoverflow.com/questions/38050649
    source_lines, _ = get_source_lines(func)
    source_lines = itertools.dropwhile(lambda x: x.strip().startswith("@"), source_lines)
    line = next(source_lines).strip()  # type: ignore
    if not line.startswith(("def ", "class ")):
        return line.rsplit(":")[-1].strip()
    if not line.endswith(":"):
        for line in source_lines:
            line = line.strip()
            if line.endswith(":"):
                break
    return "".join(source_lines)


def get_deprecated_message(obj) -> str | None:
    """Return deprecated message (created by deprecated decorator).

    Arguments:
        obj: Object to check
    """
    return obj.__deprecated__ if hasattr(obj, "__deprecated__") else None


@functools.cache
def get_doc(
    obj,
    *,
    escape: bool = False,
    fallback: str = "",
    from_base_classes: bool = False,
    only_summary: bool = False,
) -> str:
    """Get __doc__ for given object.

    Arguments:
        obj: Object to get docstrings from
        escape: Whether docstrings should get escaped
        fallback: Fallback in case docstrings dont exist
        from_base_classes: Use base class docstrings if docstrings dont exist
        only_summary: Only return first line of docstrings
    """
    if from_base_classes:
        doc = inspect.getdoc(obj)
    else:
        doc = inspect.cleandoc(obj.__doc__) if isinstance(obj.__doc__, str) else None
    if not doc:
        return fallback
    if only_summary:
        doc = doc.split("\n")[0]
    return helpers.escaped(doc) if doc and escape else doc


@functools.cache
def get_source(obj: datatypes.HasCodeType) -> str:
    """Cached wrapper for inspect.getsource.

    Arguments:
        obj: Object to return source for.
    """
    return inspect.getsource(obj)


@functools.cache
def get_source_lines(obj: datatypes.HasCodeType) -> tuple[list[str], int]:
    """Cached wrapper for inspect.getsourcelines.

    Arguments:
        obj: Object to return source lines for.
    """
    return inspect.getsourcelines(obj)


@functools.cache
def get_file(obj: datatypes.HasCodeType) -> pathlib.Path | None:
    """Cached wrapper for inspect.getfile.

    Arguments:
        obj: Object to get file for
    """
    with contextlib.suppress(TypeError):
        return pathlib.Path(inspect.getfile(obj))
    return None
