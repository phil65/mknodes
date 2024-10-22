from __future__ import annotations

import dataclasses
import functools
import inspect
from typing import TYPE_CHECKING, Any

import griffe
from jinjarope import inspectfilters


if TYPE_CHECKING:
    import pathlib
    import types

    from mknodes.data import datatypes


def iter_code_sections(code_string: str, start_line: int | None = None):
    @dataclasses.dataclass
    class Section:
        typ: str
        code: str
        start_line: int | None = None

    lines: list[str] = []
    mode = ""
    line_num = start_line or 0
    for i, line in enumerate(code_string.split("\n"), start=line_num):
        if not line.strip() or line.rstrip().endswith("##"):
            continue
        if line.strip().startswith("#"):
            if mode == "code":
                code = "\n".join(lines)
                yield Section(mode, code, start_line=line_num if start_line else None)
                lines = []
                line_num = i
            lines.append(line.strip().removeprefix("#")[1:])
            mode = "comment"
        elif not line.strip().startswith("#"):
            if mode == "comment":
                text = "\n".join(lines)
                yield Section("comment", text)
                lines = []
                line_num = i
            lines.append(line)
            mode = "code"
    if mode == "code":
        code = "\n".join(lines)
        yield Section("code", code, start_line=line_num if start_line else None)
    elif mode == "comment":
        text = "\n".join(lines)
        yield Section("comment", text)


def get_stack_info(frame: types.FrameType | None, level: int) -> dict[str, Any] | None:
    for _ in range(level):
        assert frame
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


def get_deprecated_message(obj) -> str | None:
    """Return deprecated message (created by deprecated decorator).

    Arguments:
        obj: Object to check
    """
    if isinstance(obj, griffe.Function | griffe.Class):
        paths = [
            i for i in obj.decorators if i.callable_path == "typing_extensions.deprecated"
        ]
        if paths:
            p = str(paths[0].value)
            # ast.literal_eval(str(paths[0].value.arguments[0]))
            return p[p.find("(") + 2 : p.find(")") - 1]
    return obj.__deprecated__ if hasattr(obj, "__deprecated__") else None


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

    Arguments:
        obj: Object to return source for.
    """
    return obj.source if isinstance(obj, griffe.Object) else inspect.getsource(obj)


@functools.cache
def get_source_lines(
    obj: datatypes.HasCodeType | griffe.Object,
) -> tuple[list[str], int]:
    """Cached wrapper for inspect.getsourcelines.

    Arguments:
        obj: Object to return source lines for.
    """
    if isinstance(obj, griffe.Object):
        return (obj.source.split("\n"), obj.lineno or 0)
    return inspect.getsourcelines(obj)


@functools.cache
def get_file(obj: datatypes.HasCodeType | griffe.Object) -> pathlib.Path | None:
    """Cached wrapper for inspect.getfile.

    Arguments:
        obj: Object to get file for
    """
    if isinstance(obj, griffe.Object):
        return fp[0] if isinstance(fp := obj.filepath, list) else fp
    return inspectfilters.get_file(obj)


def get_argspec(obj, remove_self: bool = True) -> inspect.FullArgSpec:
    """Return a cleaned-up FullArgSpec for given callable.

    ArgSpec is cleaned up by removing `self` from method callables.

    Arguments:
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
