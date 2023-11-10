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

import griffe

from mknodes.utils import log


T = typing.TypeVar("T", bound=type)


logger = log.get_logger(__name__)


@functools.cache
def list_subclasses(
    klass: T,
    *,
    recursive: bool = True,
    filter_abstract: bool = False,
    filter_generic: bool = True,
    filter_locals: bool = True,
) -> list[T]:
    """Return list of all subclasses of given klass.

    Note: This call is cached. Consider iter_subclasses for uncached iterating.

    Arguments:
        klass: class to get subclasses from
        filter_abstract: whether abstract base classes should be included.
        filter_generic: whether generic base classes should be included.
        filter_locals: whether local base classes should be included.
        recursive: whether to also get subclasses of subclasses.
    """
    return list(
        iter_subclasses(
            klass,
            recursive=recursive,
            filter_abstract=filter_abstract,
            filter_generic=filter_generic,
            filter_locals=filter_locals,
        )
    )


T = typing.TypeVar("T", bound=type)


def iter_subclasses(
    klass: T,
    *,
    recursive: bool = True,
    filter_abstract: bool = False,
    filter_generic: bool = True,
    filter_locals: bool = True,
) -> typing.Iterator[T]:
    """(Recursively) iterate all subclasses of given klass.

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


def iter_baseclasses(
    klass: T,
    *,
    recursive: bool = True,
    filter_abstract: bool = False,
    filter_generic: bool = True,
    filter_locals: bool = True,
) -> typing.Iterator[T]:
    """(Recursively) iterate all baseclasses of given klass.

    Arguments:
        klass: class to get subclasses from
        filter_abstract: whether abstract base classes should be included.
        filter_generic: whether generic base classes should be included.
        filter_locals: whether local base classes should be included.
        recursive: whether to also get baseclasses of baseclasses.
    """
    for kls in klass.__bases__:
        if recursive:
            yield from iter_baseclasses(kls)
        if filter_abstract and inspect.isabstract(kls):
            continue
        if filter_generic and kls.__qualname__.endswith("]"):
            continue
        if filter_locals and "<locals>" in kls.__qualname__:
            continue
        yield kls


@functools.cache
def list_baseclasses(
    klass: T,
    *,
    recursive: bool = True,
    filter_abstract: bool = False,
    filter_generic: bool = True,
    filter_locals: bool = True,
) -> list[T]:
    """Return list of all baseclasses of given klass.

    Arguments:
        klass: class to get subclasses from
        filter_abstract: whether abstract base classes should be included.
        filter_generic: whether generic base classes should be included.
        filter_locals: whether local base classes should be included.
        recursive: whether to also get baseclasses of baseclasses.
    """
    return list(
        iter_baseclasses(
            klass,
            recursive=recursive,
            filter_abstract=filter_abstract,
            filter_generic=filter_generic,
            filter_locals=filter_locals,
        )
    )


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
    """Return a module for given module path. If module is given, just return it.

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

    Arguments:
        klass: Name / path to get a klass for
    """
    match klass:
        case type():
            return klass
        case str() if ":" in klass:
            # path.to.mod:Classname
            mod_path, klass_name = klass.split(":", maxsplit=1)
            mod = import_module(mod_path)
            return getattr(mod, klass_name)
        case str():
            # path.to.mod.Classname
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
        case griffe.Object():
            return obj.canonical_path
        case _:
            raise TypeError(obj)


@functools.cache
def list_classes(
    module: types.ModuleType | str | tuple[str, ...],
    *,
    type_filter: type | None | types.UnionType = None,
    module_filter: str | None = None,
    filter_by___all__: bool = False,
    recursive: bool = False,
) -> list[type]:
    """Return list of classes from given module.

    Arguments:
        module: either a module or a path to a module in form of str or
                tuple of strings.
        type_filter: only return classes which are subclasses of given type.
        module_filter: filter by a module prefix.
        filter_by___all__: Whether to filter based on whats defined in __all__.
        recursive: import all submodules recursively and also return their classes.
    """
    return list(
        iter_classes(
            module=module,
            type_filter=type_filter,
            module_filter=module_filter,
            filter_by___all__=filter_by___all__,
            recursive=recursive,
        )
    )


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
        for submod in get_submodules(mod):
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
    # import pkgutil

    # for _importer, mod_name, _ispkg in pkgutil.iter_modules(module.__path__):
    #     yield importlib.import_module(f"{module.__name__}.{mod_name}")
    return [
        mod
        for name, mod in get_members(module, inspect.ismodule)
        if name.startswith(module.__name__)
    ]


@functools.cache
def import_module(mod: str) -> types.ModuleType:
    """Cached version of importlib.import_module.

    Arguments:
        mod: The module to import.
    """
    return importlib.import_module(mod)


@functools.cache
def get_members(obj: object, predicate: Callable | None = None):
    """Cached version of inspect.getmembers.

    Arguments:
        obj: Object to get members for
        predicate: Optional predicate for the members
    """
    return inspect.getmembers(obj, predicate)


@functools.cache
def import_file(path: str | os.PathLike) -> types.ModuleType:
    """Import a module based on a file path.

    Arguments:
        path: Path which should get imported
    """
    p = pathlib.Path(path)
    if p.is_dir():
        msg = f"{path!r} is a directory."
        raise IsADirectoryError(msg)
    module_name = p.stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        raise RuntimeError
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


@functools.cache
def to_callable(path: str | Callable) -> Callable:
    """Return a callable from a string describing the path to a Callable.

    If path already is a callable, return it without changes.
    Must be of format "module.path:object.fn"

    Arguments:
        path: The path to the callable to return.
    """
    if callable(path):
        return path
    modname, _sep, qualname = path.partition(":")
    obj = import_file(modname) if modname.endswith(".py") else import_module(modname)
    for attr in qualname.split("."):
        obj = getattr(obj, attr)
    if not callable(obj):
        msg = "Incorrect path"
        raise TypeError(msg)
    return obj


def get_code_name(obj) -> str:
    """Get a title for an object representing code.

    Arguments:
        obj: The object to get a name for.
    """
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

    # def collect_modules(
    #     self,
    #     *,
    #     recursive: bool = False,
    #     predicate: Callable[[types.ModuleType], bool] | None = None,
    #     submodule: types.ModuleType | str | tuple | list | None = None,
    # ):
    #     """Collect submodules.

    #     Arguments:
    #         recursive: Collect recursively
    #         predicate: Module filter predicate
    #         submodule: Module to collect from. If None, collect from project module.
    #     """
    #     for module in self.iter_modules(
    #         recursive=recursive,
    #         predicate=predicate,
    #         submodule=submodule,
    #     ):
    #         self.submodules.add(module)

    # def iter_modules(
    #     self,
    #     *,
    #     submodule: types.ModuleType | str | tuple | list | None = None,
    #     recursive: bool = False,
    #     predicate: Callable[[types.ModuleType], bool] | None = None,
    #     _seen: set | None = None,
    # ) -> Iterator[types.ModuleType]:
    #     """Iterate over all submodules of the module.

    #     Arguments:
    #         submodule: filter based on a submodule
    #         recursive: whether to only iterate over members of current module
    #                    or whether it should also include modules from submodules.
    #         predicate: filter modules based on a predicate.
    #     """
    #     mod = classhelpers.to_module(submodule) if submodule else self.module
    #     seen = _seen or set()
    #     if mod is None:
    #         return
    #     for submod_name, submod in inspect.getmembers(mod, inspect.ismodule):
    #         not_in_all = hasattr(mod, "__all__") and submod_name not in mod.__all__
    #         filtered_by_all = self.filter_by___all__ and not_in_all
    #         not_filtered_by_pred = predicate(submod) if predicate else True
    #         # if self.module_name in mod.__name__.split(".")
    #         if not filtered_by_all and not_filtered_by_pred:
    #             yield submod
    #         if recursive and submod not in seen:
    #             seen.add(submod)
    #             yield from self.iter_modules(
    #                 submodule=submod,
    #                 recursive=True,
    #                 predicate=predicate,
    #                 _seen=seen,
    #             )


if __name__ == "__main__":
    import mknodes as mk

    print(get_topmost_module_path(mk.MkCode.for_object))
    print(mk.MkCode.for_object.__qualname__)
