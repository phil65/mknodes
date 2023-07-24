from __future__ import annotations

from collections.abc import Iterator, Sequence
import contextlib
import importlib
import inspect
import logging
import pathlib
import types
import typing


T = typing.TypeVar("T", bound=type)


logger = logging.getLogger(__name__)


def get_subclasses(klass: type, include_abstract: bool = False) -> typing.Iterator[type]:
    """Recursively iter all subclasses of given klass.

    Arguments:
        klass: class to get subclasses from
        include_abstract: whether abstract base classes should be included.
    """
    if getattr(klass.__subclasses__, "__self__", None) is None:
        return
    for i in klass.__subclasses__():
        yield from get_subclasses(i)
        if include_abstract or not inspect.isabstract(i):
            yield i


@typing.overload
def to_module(module, return_none: typing.Literal[False] = ...) -> types.ModuleType:
    ...


@typing.overload
def to_module(module, return_none: typing.Literal[True] = ...) -> types.ModuleType | None:
    ...


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
        case (str(), *_) | str():
            module_path = module if isinstance(module, str) else ".".join(module)
            try:
                return importlib.import_module(module_path)
            except (ImportError, AttributeError) as e:
                logger.warning("Could not import %s", module_path)
                if return_none:
                    return None
                raise ImportError from e
        case types.ModuleType():
            return module
        case _:
            raise TypeError(module)


def to_class(klass: type | str | tuple[str, ...] | list[str]):
    match klass:
        case type():
            return klass
        case str():
            parts = klass.split(".")
            mod = importlib.import_module(".".join(parts[:-1]))
            return getattr(mod, parts[-1])
        case tuple() | list():
            mod = importlib.import_module(".".join(klass[:-1]))
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
        case (str(), *_):
            return tuple(module)
        case str():
            return tuple(module.split("."))
        case types.ModuleType():
            return tuple(module.__name__.split("."))
        case pathlib.Path() if not module.is_absolute():
            return module.parts
        case _:
            raise TypeError(module)


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
        for _name, submod in inspect.getmembers(mod, inspect.ismodule):
            if submod.__name__.startswith(module_filter or ""):
                yield from iter_classes(
                    submod,
                    type_filter=type_filter,
                    module_filter=submod.__name__,
                    filter_by___all__=filter_by___all__,
                    recursive=True,
                )
    for klass_name, kls in inspect.getmembers(mod, inspect.isclass):
        has_all = hasattr(mod, "__all__")
        if filter_by___all__ and (not has_all or klass_name not in mod.__all__):
            continue
        if type_filter is not None and not issubclass(kls, type_filter):
            continue
        if module_filter is not None and not kls.__module__.startswith(module_filter):
            continue
        yield kls


def get_topmost_module_path(obj: type | types.FunctionType | types.MethodType) -> str:
    """Return path of topmost module containing given class.

    If a class is imported in any of its parent modules, return that "shorter" path.

    So for a class "submodule.classmodule.Class", it could return "submodule.Class"

    Arguments:
        obj: Klass to get the path for.
    """
    path = obj.__module__
    match obj:
        case type():
            fn = inspect.isclass
        case types.MethodType():
            fn = inspect.ismethod
        case types.FunctionType():
            fn = inspect.isfunction
    parts = path.split(".")
    while parts:
        with contextlib.suppress(TypeError):
            new_path = ".".join(parts)
            mod = importlib.import_module(new_path)
            objs = [i for _i_name, i in inspect.getmembers(mod, fn)]
            if obj in objs:
                path = new_path
        parts = parts[:-1]
    return path


if __name__ == "__main__":
    from prettyqt import widgets

    path = iter_classes(widgets, recursive=False)
    print(len(list(path)))
