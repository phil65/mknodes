from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
import contextlib
import functools
import importlib
import importlib.util
import inspect
import os
import pathlib
import sys
import types
import typing

from mknodes.utils import log


T = typing.TypeVar("T", bound=type)


logger = log.get_logger(__name__)


def iter_subclasses(
    klass: T,
    *,
    recursive: bool = True,
    filter_abstract: bool = False,
    filter_generic: bool = True,
    filter_locals: bool = True,
) -> typing.Iterator[T]:
    """Recursively iter all subclasses of given klass.

    Arguments:
        klass: class to get subclasses from
        filter_abstract: whether abstract base classes should be included.
        filter_generic: whether generic base classes should be included.
        filter_locals: whether local base classes should be included.
        recursive: whether to also get subclasses of subclasses.
    """
    if getattr(klass.__subclasses__, "__self__", None) is None:
        return
    for kls in klass.__subclasses__():
        if recursive:
            yield from iter_subclasses(kls)
        if filter_abstract and inspect.isabstract(kls):
            continue
        if filter_generic and kls.__qualname__.endswith("]"):
            continue
        if filter_locals and "<locals>" in kls.__qualname__:
            continue
        yield kls


@typing.overload
def to_module(module, return_none: typing.Literal[False] = ...) -> types.ModuleType: ...


@typing.overload
def to_module(
    module,
    return_none: typing.Literal[True] = ...,
) -> types.ModuleType | None: ...


@functools.cache
def to_module(
    module: str | Sequence[str] | types.ModuleType,
    return_none: bool = True,
) -> types.ModuleType | None:
    """Returns a module for given module path. If module is given, just return it.

    Arguments:
        module: A ModuleType, str or sequence.
        return_none: In case module cant get imported, return None.
                     If False, Exception is thrown.
    """
    match module:
        case (str(), *_) | str():  # type: ignore[attr-defined]
            module_path = module if isinstance(module, str) else ".".join(module)
            try:
                return import_module(module_path)
            except (ImportError, AttributeError) as e:
                logger.warning("Could not import %s", module_path)
                if return_none:
                    return None
                raise ImportError from e
        case types.ModuleType():
            return module
        case _:
            raise TypeError(module)


@functools.cache
def to_class(klass: type | str | tuple[str, ...] | list[str]):
    """Convert given input to a class.

    If input is a string or Sequence, interpret it as a dotted path.
    """
    match klass:
        case type():
            return klass
        case str():
            parts = klass.split(".")
            mod = import_module(".".join(parts[:-1]))
            return getattr(mod, parts[-1])
        case tuple() | list():
            mod = import_module(".".join(klass[:-1]))
            return getattr(mod, klass[-1])
        case _:
            raise TypeError(klass)


def to_module_parts(  # type: ignore
    module: Sequence[str] | str | types.ModuleType,
) -> tuple[str, ...]:
    """Returns a tuple describing the module path.

    Result is of form ("module", "submodule", "subsubmodule")

    Arguments:
        module: A ModuleType, str or sequence.
    """
    match module:
        case (str(), *_):  # type: ignore[attr-defined]
            return tuple(module)
        case str():
            return tuple(module.split("."))
        case types.ModuleType():
            return tuple(module.__name__.split("."))
        case pathlib.Path() if not module.is_absolute():
            return module.parts
        case _:
            raise TypeError(module)


def to_dotted_path(
    obj: Sequence[str] | str | types.ModuleType | types.MethodType | type,
) -> str:
    """Return dotted path for given input.

    Arguments:
        obj: Input to return dotted path for
    """
    match obj:
        case (str(), *_):  # type: ignore[attr-defined]
            return ".".join(obj)
        case str():
            return obj
        case types.ModuleType():
            return obj.__name__
        case type() | Callable():
            return f"{obj.__module__}.{obj.__qualname__}"
        case _:
            raise TypeError(obj)


@functools.cache
def iter_classes(
    module: types.ModuleType | str | tuple[str, ...],
    *,
    type_filter: type | None | types.UnionType = None,
    module_filter: str | None = None,
    filter_by___all__: bool = False,
    recursive: bool = False,
) -> Iterator[type]:
    """Yield classes from given module.

    Arguments:
        module: either a module or a path to a module in form of str or
                tuple of strings.
        type_filter: only yield classes which are subclasses of given type.
        module_filter: filter by a module prefix.
        filter_by___all__: Whether to filter based on whats defined in __all__.
        recursive: import all submodules recursively and also yield their classes.
    """
    mod = to_module(module)
    if not mod:
        return []
    if recursive:
        for _name, submod in get_members(mod, inspect.ismodule):
            if submod.__name__.startswith(module_filter or ""):
                yield from iter_classes(
                    submod,
                    type_filter=type_filter,
                    module_filter=submod.__name__,
                    filter_by___all__=filter_by___all__,
                    recursive=True,
                )
    for klass_name, kls in get_members(mod, inspect.isclass):
        has_all = hasattr(mod, "__all__")
        if filter_by___all__ and (not has_all or klass_name not in mod.__all__):
            continue
        if type_filter is not None and not issubclass(kls, type_filter):
            continue
        if module_filter is not None and not kls.__module__.startswith(module_filter):
            continue
        yield kls


@functools.cache
def get_topmost_module_path(obj: Callable) -> str:
    """Return path of topmost module containing given class.

    If a class is imported in any of its parent modules, return that "shorter" path.

    So for a class "submodule.classmodule.Class", it could return "submodule.Class"

    Arguments:
        obj: Klass to get the path for.
    """
    to_search_for = obj.__self__ if hasattr(obj, "__self__") else obj
    path = obj.__module__
    parts = path.split(".")
    while parts:
        with contextlib.suppress(TypeError):
            new_path = ".".join(parts)
            mod = import_module(new_path)
            objs = [i for _i_name, i in get_members(mod)]
            if to_search_for in objs:
                path = new_path
        parts = parts[:-1]
    return path


@functools.cache
def get_submodules(
    module: types.ModuleType | str | tuple[str, ...],
) -> list[types.ModuleType]:
    """Return list of submodules of given module.

    Arguments:
        module: Module to return submodules from.
    """
    module = to_module(module)
    return [
        mod
        for name, mod in get_members(module, inspect.ismodule)
        if name.startswith(module.__name__)
    ]


@functools.cache
def import_module(mod: str):
    return importlib.import_module(mod)


@functools.cache
def get_members(module, predicate=None):
    return inspect.getmembers(module, predicate)


@functools.cache
def import_file(path: str | os.PathLike) -> types.ModuleType:
    """Import a module based on a file path.

    Arguments:
        path: Path which should get imported
    """
    module_name = pathlib.Path(path).stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        raise RuntimeError
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


@functools.cache
def to_callable(path: str | Callable) -> Callable:
    if callable(path):
        return path
    modname, _qualname_separator, qualname = path.partition(":")
    obj = import_file(modname) if modname.endswith(".py") else import_module(modname)
    for attr in qualname.split("."):
        obj = getattr(obj, attr)
    if not callable(obj):
        msg = "Incorrect path"
        raise TypeError(msg)
    return obj


def get_code_name(obj) -> str:
    """Get a title for an object representing code."""
    match obj:
        case types.CodeType():
            return obj.co_name
        case types.TracebackType():
            return obj.tb_frame.f_code.co_name
        case types.FrameType():
            return obj.f_code.co_name
        case Callable():
            return to_dotted_path(obj)
        case _:
            return obj.__name__


if __name__ == "__main__":
    import mknodes

    print(get_topmost_module_path(mknodes.MkCode.for_object))
    print(mknodes.MkCode.for_object.__qualname__)
