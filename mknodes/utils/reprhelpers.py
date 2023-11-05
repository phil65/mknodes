from __future__ import annotations

import dataclasses

from operator import attrgetter
import os
import reprlib
from typing import Any

from mknodes.data import datatypes
from mknodes.utils import inspecthelpers, log


logger = log.get_logger(__name__)


class LengthLimitRepr(reprlib.Repr):
    def repr_type(self, obj, level):
        return obj.__name__

    def repr_module(self, obj, level):
        return obj.__name__

    def repr_function(self, obj, level):
        return obj.__name__

    def repr_method(self, obj, level):
        return f"{obj.__self__.__class__.__name__}.{obj.__name__}"


limit_repr = LengthLimitRepr()
limit_repr.maxlist = 10
limit_repr.maxstring = 100
limit_repr.maxlevel = 8
limit_repr.maxtuple = 10
limit_repr.maxarray = 10
limit_repr.maxdict = 10
limit_repr.maxset = 10
limit_repr.maxfrozenset = 10
limit_repr.maxdeque = 10
limit_repr.maxlong = 60
limit_repr.maxother = 60


def get_repr(
    _obj: Any,
    *args: Any,
    _shorten: bool = True,
    _filter_empty: bool = False,
    _filter_false: bool = False,
    _char_width: int | None = None,
    **kwargs: Any,
) -> str:
    """Get a suitable __repr__ string for an object.

    This function can be used to manually construct reprs. For automatic reprs,
    see `get_nondefault_repr` and `get_dataclass_repr`.

    Args:
        _obj: The object to get a repr for.
        *args: Arguments for the repr
        _shorten: Whether to shorten the repr.
        _filter_empty: Filter kwargs  with None, empty str / empty dicts as value
        _filter_false: Filter False values
        _char_width: If set, then repr will be formatted with black to given char width
        **kwargs: Keyword arguments for the repr
    """
    my_repr = limit_repr.repr if _shorten else repr
    classname = type(_obj).__name__
    parts = [list_repr(v) if isinstance(v, list) else my_repr(v) for v in args]
    kw_parts = []
    for k, v in kwargs.items():
        if _filter_empty and (v is None or v == "" or v == {}):
            continue
        if _filter_false and v is False:
            continue

        import mknodes as mk

        match v:
            case (mk.MkNode(), *_):
                name = list_repr(v)
            case os.PathLike():
                name = repr(os.fspath(v))
            case _:
                name = my_repr(v)
        kw_parts.append(f"{k}={name}")
    sig = ", ".join(parts + kw_parts)
    text = f"{classname}({sig})"
    if _char_width:
        from mkdocstrings_handlers.python import rendering

        return rendering.do_format_code(text, _char_width)
    return text


def list_repr(v, shorten: bool = True):
    import mknodes as mk

    my_repr = limit_repr.repr if shorten else repr
    match v:
        case (mk.MkNode(), *_) if len(v) > 1 and any(i.children for i in v):
            return "[...]"
        case (mk.MkNode(),):
            if type(v[0]) in {mk.MkText, mk.MkHeader}:
                return my_repr(str(v[0]))
            # if isinstance(v[0], mk.MkContainer) and len(v[0].items) == 1:
            #     pass
            return f"[{v.__class__.__name__}([...])]"
            # val = str(v[0]) if type(v[0]) in {mk.MkText, mk.MkHeader} else v[0]
            # return my_repr(val)
        case _:
            return my_repr(v)


def get_dataclass_repr(
    instance: datatypes.DataclassInstance,
    char_width: int | None = None,
) -> str:
    """Return repr for dataclass, filtered by non-default values.

    Arguments:
        instance: dataclass instance
        char_width: If set, then repr will be formatted with black to given char width
    """
    vals = []
    for f in dataclasses.fields(instance):
        no_default = isinstance(f.default, dataclasses._MISSING_TYPE)
        no_default_factory = isinstance(f.default_factory, dataclasses._MISSING_TYPE)
        if not no_default:
            val = attrgetter(f.name)(instance)
            if val != f.default:
                vals.append((f.name, val))
        if not no_default_factory:
            val = attrgetter(f.name)(instance)
            if val != f.default_factory():
                vals.append((f.name, val))
        if no_default and no_default_factory:
            val = attrgetter(f.name)(instance)
            vals.append((f.name, val))
    nodef_f_repr = ", ".join(f"{name}={value!r}" for name, value in vals)
    text = f"{instance.__class__.__name__}({nodef_f_repr})"
    if char_width:
        from mkdocstrings_handlers.python import rendering

        return rendering.do_format_code(text, char_width)
    return text


def to_str_if_textnode(node) -> str:
    import mknodes as mk

    return str(node) if type(node) in {mk.MkText, mk.MkHeader} else node


def get_nondefault_repr(
    instance: object,
    char_width: int | None = 60,
    shorten: bool = False,
) -> str:
    """Get a repr for an instance containing all nondefault (keyword) arguments.

    The instance is checked for keyword-named attributes with "_" prepended first.
    If that doesnt exist, it fallbacks to keyword-name = argument name.

    Examples:
        Here the repr will contain the kwarg `some_value` with type `int` because
        "_"-prefixed is preferred.
        ```
        def __init__(self, some_value: int = 0):
            self._some_value = some_value
            self.some_value = str(some_value)
        ```

    Arguments:
        instance: The instance to get a repr for
        char_width: If set, then repr will be formatted with black to given char width
        shorten: Whether to shorten the repr using a custom reprlib Repr
    """
    spec = inspecthelpers.get_argspec(instance.__init__)
    args = []
    for arg in spec.args:
        if arg == "content":
            val = getattr(instance, "items", None)
        elif hasattr(instance, f"_{arg}"):
            val = getattr(instance, f"_{arg}")
        else:
            val = getattr(instance, arg)
        args.append(val)
    dct = spec.kwonlydefaults or {}
    kwargs = {}
    for k, v in dct.items():
        # check for hidden attribute first, then for attribute named like kwarg
        if f"_{k}" in instance.__dict__ and v != getattr(instance, f"_{k}"):
            kwargs[k] = getattr(instance, f"_{k}")
        elif k in instance.__dict__ and v != getattr(instance, k):
            kwargs[k] = getattr(instance, k)
    return get_repr(instance, *args, **kwargs, _char_width=char_width, _shorten=shorten)


if __name__ == "__main__":
    import mknodes as mk

    node = mk.MkAdmonition("test", typ="info", collapsible=True)
    print(repr(node))
