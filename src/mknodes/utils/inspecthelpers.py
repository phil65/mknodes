import functools
import inspect
from typing import TYPE_CHECKING, Any

import griffe
from jinjarope import inspectfilters


if TYPE_CHECKING:
    from collections.abc import Callable
    import pathlib
    import types

    from mknodes.data import datatypes


def get_stack_info(frame: types.FrameType | None, level: int) -> dict[str, Any] | None:
    for _ in range(level):
        assert frame
        frame = frame.f_back
    if not frame:
        return None
    return _frame_info(frame)


def _frame_info(frame: types.FrameType) -> dict[str, Any]:
    fn_name = qual if (qual := frame.f_code.co_qualname) != "<module>" else None
    return dict(
        source_filename=frame.f_code.co_filename,
        source_function=fn_name,
        source_line_no=frame.f_lineno,
    )


# Packages whose frames sit between user code and a node constructor: event loop /
# thread machinery (route functions run in threads and via `anyenv.run_sync`) and
# template engines.
_INFRASTRUCTURE_PACKAGES = frozenset({
    "anyenv",
    "anyio",
    "asyncio",
    "concurrent",
    "contextlib",
    "contextvars",
    "functools",
    "jinja2",
    "jinjarope",
    "logfire",
    "threading",
})


def _is_internal_module(module: str) -> bool:
    # The manual (mknodes' own docs) is user code.
    if module.startswith("mknodes.manual"):
        return False
    if module == "mknodes" or module.startswith("mknodes."):
        return True
    return module.partition(".")[0] in _INFRASTRUCTURE_PACKAGES


def get_creation_info(frame: types.FrameType | None) -> dict[str, Any] | None:
    """Return location info of the user code which caused the creation of a node.

    Walks up the stack from the caller of given frame, skipping frames of mknodes
    itself and of event loop / thread machinery.

    Args:
        frame: The frame of the constructor (usually `inspect.currentframe()`)
    """
    frame = frame.f_back if frame else None
    while frame:
        if not _is_internal_module(frame.f_globals.get("__name__") or ""):
            return _frame_info(frame)
        frame = frame.f_back
    return None


def get_callable_info(fn: Callable[..., Any]) -> dict[str, Any] | None:
    """Return location info (like `get_creation_info`) for the definition of a callable.

    Args:
        fn: The callable to get info for
    """
    code = getattr(inspect.unwrap(fn), "__code__", None)
    if code is None:
        return None
    return dict(
        source_filename=code.co_filename,
        source_function=code.co_qualname,
        source_line_no=code.co_firstlineno,
    )


def get_deprecated_message(obj: Any) -> str | None:
    """Return deprecated message (created by deprecated decorator).

    Args:
        obj: Object to check
    """
    if isinstance(obj, griffe.Function | griffe.Class):
        paths = [i for i in obj.decorators if i.callable_path == "typing_extensions.deprecated"]
        if paths:
            p = str(paths[0].value)
            # ast.literal_eval(str(paths[0].value.arguments[0]))
            return p[p.find("(") + 2 : p.find(")") - 1]
    return obj.__deprecated__ if hasattr(obj, "__deprecated__") else None  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]


def is_abstract(obj: type | griffe.Class | griffe.Function) -> bool:
    """Check whether a class / method is abstract."""
    match obj:
        case griffe.Function():
            return "abc.abstractmethod" in [i.callable_path for i in obj.decorators]
        case griffe.Class():
            bases = [i if isinstance(i, str) else i.canonical_path for i in obj.bases]
            return "abc.ABC" in bases
        case _:
            return inspect.isabstract(obj)


@functools.cache
def get_source(obj: datatypes.HasCodeType | griffe.Object) -> str:
    """Cached wrapper for inspect.getsource.

    Args:
        obj: Object to return source for.
    """
    return obj.source if isinstance(obj, griffe.Object) else inspect.getsource(obj)


@functools.cache
def get_source_lines(obj: datatypes.HasCodeType | griffe.Object) -> tuple[list[str], int]:
    """Cached wrapper for inspect.getsourcelines.

    Args:
        obj: Object to return source lines for.
    """
    if isinstance(obj, griffe.Object):
        return (obj.source.split("\n"), obj.lineno or 0)
    return inspect.getsourcelines(obj)


@functools.cache
def get_file(obj: datatypes.HasCodeType | griffe.Object) -> pathlib.Path | None:
    """Cached wrapper for inspect.getfile.

    Args:
        obj: Object to get file for
    """
    if isinstance(obj, griffe.Object):
        return fp[0] if isinstance(fp := obj.filepath, list) else fp
    return inspectfilters.get_file(obj)


def get_argspec(obj: Any, remove_self: bool = True) -> inspect.FullArgSpec:
    """Return a cleaned-up FullArgSpec for given callable.

    ArgSpec is cleaned up by removing `self` from method callables.

    Args:
        obj: A callable python object
        remove_self: Whether to remove "self" argument from method argspecs
    """
    # if isinstance(obj, griffe.Function):
    #     args = [i for i in obj.parameters if i.kind == "positional-only"]
    #     varargs = [i for i in obj.parameters if i.kind == "variadic positional"]
    #     varkw = [i for i in obj.parameters if i.kind == "variadic keyword"]
    #     kw_only = [i for i in obj.parameters if i.kind == "keyword-only"]
    #     spec = inspect.FullArgSpec(args, varargs, varkw, (), kw_only)
    return inspectfilters.get_argspec(obj, remove_self)
