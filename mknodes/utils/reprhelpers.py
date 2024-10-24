from __future__ import annotations

import os
import reprlib
from typing import TYPE_CHECKING, Any

from jinjarope import inspectfilters, textfilters, utils

from mknodes.utils import log


if TYPE_CHECKING:
    from mknodes.data import datatypes


logger = log.get_logger(__name__)


class LengthLimitRepr(reprlib.Repr):
    """Custom repr."""

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
    kw_parts: list[str] = []
    for k, v in kwargs.items():
        if _filter_empty and (v is None or v in ("", {})):
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
        return textfilters.format_code(text, _char_width)
    return text


def list_repr(v: Any, shorten: bool = True):
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
    vals = utils.get_dataclass_nondefault_values(instance)
    nodef_f_repr = ", ".join(f"{name}={value!r}" for name, value in vals.items())
    text = f"{instance.__class__.__name__}({nodef_f_repr})"
    if char_width:
        return textfilters.format_code(text, char_width)
    return text


def to_str_if_textnode(node: Any) -> str:
    import mknodes as mk

    return str(node) if type(node) in {mk.MkText, mk.MkHeader} else node


def get_nondefault_repr(
    instance: object,
    char_width: int | None = None,
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
    args: list[Any] = []
    kwargs: dict[str, Any] = {}
    signature = inspectfilters.get_signature(instance.__init__)
    for arg, v in signature.parameters.items():
        if v.kind in {v.VAR_POSITIONAL, v.VAR_KEYWORD}:
            continue
        if arg == "content":
            val = getattr(instance, "items", None)
        elif hasattr(instance, f"_{arg}"):
            val = getattr(instance, f"_{arg}")
        else:
            val = getattr(instance, arg)
        if v.default != val:
            if v.kind in {v.KEYWORD_ONLY}:
                kwargs[arg] = val
            if v.kind in {v.POSITIONAL_OR_KEYWORD, v.POSITIONAL_ONLY}:
                args.append(val)
    return get_repr(instance, *args, _char_width=char_width, _shorten=shorten, **kwargs)  # type: ignore[arg-type]


if __name__ == "__main__":
    import mknodes as mk

    node = mk.MkAdmonition("test", typ="info", collapsible=True)
    print(repr(node))
