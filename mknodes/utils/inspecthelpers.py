from __future__ import annotations

import contextlib
import functools
import inspect
import itertools
import pathlib
import types

from mknodes.data import datatypes
from mknodes.utils import helpers


def get_stack_info(frame, level: int) -> dict | None:
    for _ in range(level):
        frame = frame.f_back
    if not frame:
        return None
    fn_name = qual if (qual := frame.f_code.co_qualname) != "<module>" else None
    return dict(
        source_filename=frame.f_code.co_filename,
        source_function=fn_name,
        source_line_no=frame.f_lineno,
        # klass=frame.f_locals["self"].__class__.__name__,
    )


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


def get_argspec(callable_obj) -> inspect.FullArgSpec:
    """Return a cleanup-up FullArgSpec for given callable.

    ArgSpec is cleaned up by removing self from method callables.

    Arguments:
        callable_obj: A callable python object
    """
    if inspect.isfunction(callable_obj):
        argspec = inspect.getfullargspec(callable_obj)
    elif inspect.ismethod(callable_obj):
        argspec = inspect.getfullargspec(callable_obj)
        del argspec.args[0]  # remove "self"
    elif inspect.isclass(callable_obj):
        if callable_obj.__init__ is object.__init__:  # to avoid an error
            argspec = inspect.getfullargspec(lambda self: None)
        else:
            argspec = inspect.getfullargspec(callable_obj.__init__)
        del argspec.args[0]  # remove "self"
    elif callable(callable_obj):
        argspec = inspect.getfullargspec(callable_obj.__call__)
        del argspec.args[0]  # remove "self"
    else:
        msg = f"{callable_obj} is not callable"
        raise TypeError(msg)
    return argspec
