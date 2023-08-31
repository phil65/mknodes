from __future__ import annotations

from collections.abc import Callable, Generator, Iterable
import contextlib
import functools
import inspect
import itertools
import logging
import os
import pathlib
import re
import reprlib
import types

from typing import Any, Literal, TypeVar

import requests

from mknodes.data import datatypes


RESPONSE_CODE_OK = 200

logger = logging.getLogger(__name__)


class LengthLimitRepr(reprlib.Repr):
    def repr_type(self, obj, level):
        return obj.__name__

    def repr_module(self, obj, level):
        return obj.__name__

    def repr_function(self, obj, level):
        return obj.__name__


limit_repr = LengthLimitRepr()
limit_repr.maxlist = 10
limit_repr.maxstring = 80


def to_str_if_textnode(node):
    import mknodes

    return str(node) if type(node) in {mknodes.MkText, mknodes.MkHeader} else node


def find_file_in_folder_or_parent(
    filename: str | pathlib.Path,
    folder: os.PathLike | str = ".",
) -> pathlib.Path | None:
    """Search for a file with given name in folder and its parent folders.

    Arguments:
        filename: File to search
        folder: Folder to start searching from
    """
    path = pathlib.Path(folder).absolute()
    while not (path / filename).exists() and len(path.parts) > 1:
        path = path.parent
    return file if (file := (path / filename)).exists() else None


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
        _shorten: Whether to shorten the repr.
        *args: Arguments for the repr
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
        name = my_repr(v)
        kw_parts.append(f"{k}={name}")
    sig = ", ".join(parts + kw_parts)
    return f"{classname}({sig})"


def escaped(text: str, entity_type: str | None = None) -> str:
    """Helper function to escape markup.

    Args:
        text: The text.
        entity_type: For the entity types ``PRE``, ``CODE`` and the link
                     part of ``TEXT_LINKS``, only certain characters need to be escaped.
    """
    if entity_type in ["pre", "code"]:
        escape_chars = r"\`"
    elif entity_type == "text_link":
        escape_chars = r"\)"
    else:
        escape_chars = r"_*[]()~`>#+-=|{}.!"

    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


def slugify(text: str | os.PathLike) -> str:
    """Create a slug for given text.

    Returned text only contains alphanumerical and underscore.

    Arguments:
        text: text to get a slug for
    """
    text = str(text).lower()
    text = re.sub("[^0-9a-zA-Z_.]", "_", text)
    return re.sub("^[^a-zA-Z_#]+", "", text)


def groupby(data, keyfunc: Callable | None = None) -> dict[str, list]:
    data = sorted(data, key=keyfunc or (lambda x: x))
    return {k: list(g) for k, g in itertools.groupby(data, keyfunc)}


def groupby_first_letter(data, keyfunc: Callable | None = None) -> dict[str, list]:
    data = sorted(data, key=keyfunc or (lambda x: x))

    def first_letter(x):
        return keyfunc(x)[0] if keyfunc else x[0]

    return {k: list(g) for k, g in itertools.groupby(data, first_letter)}


def styled(
    text: str,
    *,
    size: int | None = None,
    bold: bool = False,
    italic: bool = False,
    code: bool = False,
) -> str:
    """Apply styling to given markdown.

    Arguments:
        text: Text to style
        size: Optional text size
        bold: Whether styled text should be bold
        italic: Whether styled text should be italic
        code: Whether styled text should styled as (inline) code
    """
    if size:
        text = f"<font size='{size}'>{text}</font>"
    if bold:
        text = f"**{text}**"
    if italic:
        text = f"*{text}*"
    if code:
        text = f"`{text}`"
    return text


def label_for_class(klass: type) -> str:
    mod = klass.__module__
    parts = mod.split(".")
    if mod.startswith("prettyqt."):
        return f"{parts[1]}.{klass.__name__}"
    return f"{parts[-1]}.{klass.__name__}"


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
    return escaped(doc) if doc and escape else doc


def get_material_icon_folder() -> pathlib.Path:
    import material

    path = pathlib.Path(material.__path__[0])
    return path / ".icons"


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
def get_file(obj: datatypes.HasCodeType) -> str | None:
    """Cached wrapper for inspect.getfile.

    Arguments:
        obj: Object to get file for
    """
    with contextlib.suppress(TypeError):
        return inspect.getfile(obj)
    return None


@functools.cache
def download(url: str, typ: Literal["text", "data"] = "text"):
    if token := os.getenv("GH_TOKEN"):
        headers = {"Authorization": f"token {token}"}
        response = requests.get(url, headers=headers)
    else:
        response = requests.get(url)
    if response.status_code != RESPONSE_CODE_OK:
        return ""
    return response.text if typ == "text" else response.content


T = TypeVar("T")


def load_yaml(text: str):
    import yaml

    return yaml.load(text, Loader=yaml.FullLoader)


def dump_yaml(yaml_obj) -> str:
    import yaml

    return yaml.dump(yaml_obj, Dumper=yaml.Dumper, indent=2)


def batched(iterable: Iterable[T], n: int) -> Generator[tuple[T, ...], None, None]:
    """Batch data into tuples of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        msg = "n must be at least one"
        raise ValueError(msg)
    it = iter(iterable)
    while batch := tuple(itertools.islice(it, n)):
        yield batch


def is_url(path: str) -> bool:
    return path.startswith(("http:/", "https:/", "www."))


if __name__ == "__main__":
    strings = groupby_first_letter([str(i) for i in range(1000)])
    print(limit_repr.repr(strings))
