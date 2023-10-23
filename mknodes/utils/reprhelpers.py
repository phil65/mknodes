from __future__ import annotations

import dataclasses

from operator import attrgetter
import os
import reprlib
from typing import Any

from mknodes.data import datatypes
from mknodes.utils import log


logger = log.get_logger(__name__)


class LengthLimitRepr(reprlib.Repr):
    def repr_type(self, obj, level):
        return obj.__name__

    def repr_module(self, obj, level):
        return obj.__name__

    def repr_function(self, obj, level):
        return obj.__name__


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
    **kwargs: Any,
) -> str:
    """Get a suitable __repr__ string for an object.

    Args:
        _obj: The object to get a repr for.
        *args: Arguments for the repr
        _shorten: Whether to shorten the repr.
        _filter_empty: Filter kwargs  with None, empty str / empty dicts as value
        _filter_false: Filter False values
        **kwargs: Keyword arguments for the repr
    """
    my_repr = limit_repr.repr if _shorten else repr
    classname = type(_obj).__name__
    parts = [my_repr(val) for val in args]
    kw_parts = []
    for k, v in kwargs.items():
        if _filter_empty and (v is None or v == "" or v == {}):
            continue
        if _filter_false and v is False:
            continue

        import mknodes as mk

        match v:
            case (mk.MkNode(), *_) if len(v) > 1:
                name = "[...]"
            case os.PathLike():
                name = repr(os.fspath(v))
            case _:
                name = my_repr(v)
        kw_parts.append(f"{k}={name}")
    sig = ", ".join(parts + kw_parts)
    return f"{classname}({sig})"


def dataclass_repr(instance: datatypes.DataclassInstance) -> str:
    """Return repr for dataclass, filtered by non-default values.

    Arguments:
        instance: dataclass instance
    """
    nodef_f_vals = (
        (f.name, attrgetter(f.name)(instance))
        for f in dataclasses.fields(instance)
        if attrgetter(f.name)(instance) != f.default
    )

    nodef_f_repr = ", ".join(f"{name}={value!r}" for name, value in nodef_f_vals)
    return f"{instance.__class__.__name__}({nodef_f_repr})"


def to_str_if_textnode(node) -> str:
    import mknodes as mk

    return str(node) if type(node) in {mk.MkText, mk.MkHeader} else node


def get_nondefault_repr(instance: object) -> str:
    import inspect

    spec = inspect.getfullargspec(instance.__init__)
    spec.args.remove("self")
    args = [getattr(instance, "items" if arg == "content" else arg) for arg in spec.args]
    dct = spec.kwonlydefaults or {}
    kwargs = {
        k: getattr(instance, k)
        for k, v in dct.items()
        if k in instance.__dict__ and v != getattr(instance, k)
    }
    return get_repr(instance, *args, **kwargs)


if __name__ == "__main__":
    import mknodes as mk

    instance = mk.MkAdmonition("test", typ="info")
    print(get_nondefault_repr(instance))
