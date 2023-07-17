from __future__ import annotations

from importlib import metadata
import logging
import re
import reprlib
import sys
import textwrap
import types

from typing import Any


logger = logging.getLogger(__name__)

BASE_URL = "https://doc.qt.io/qtforpython-6/PySide6/"
BUILTIN_URL = "https://docs.python.org/3/library/{mod}.html#{name}"


class LengthLimitRepr(reprlib.Repr):
    pass


limit_repr = LengthLimitRepr()
limit_repr.maxlist = 10
limit_repr.maxstring = 80


def get_repr(_obj: Any, *args: Any, _shorten: bool = True, **kwargs: Any) -> str:
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
        if isinstance(v, type | types.ModuleType | types.MethodType | types.FunctionType):
            name = v.__name__
        else:
            name = my_repr(v)
        kw_parts.append(f"{k}={name}")
    sig = ", ".join(parts + kw_parts)
    return f"{classname}({sig})"


def escaped(text: str, entity_type: str | None = None) -> str:
    """Helper function to escape telegram markup symbols.

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


# import pathlib
# from mkdocstrings import inventory

# path = pathlib.Path(__file__, "../qt6.inv")
# with path.open("rb") as file:
#     inv = inventory.Inventory.parse_sphinx(file)

#     logger.warning(inv.values())


def linked(identifier: str, title: str | None = None) -> str:
    suffix = "" if identifier.startswith(("http:", "https:", "www.")) else ".md"
    return f"[{identifier if title is None else title}]({identifier}{suffix})"


def styled(
    text: str,
    size: int | None = None,
    bold: bool = False,
    recursive: bool = False,
    code: bool = False,
) -> str:
    if size:
        text = f"<font size='{size}'>{text}</font>"
    if bold:
        text = f"**{text}**"
    if recursive:
        text = f"*{text}*"
    if code:
        text = f"`{text}`"
    return text


def link_for_class(kls: type, **kwargs) -> str:
    if kls.__module__ == "builtins":
        url = BUILTIN_URL.format(mod="functions", name=kls.__name__)
        link = linked(url, title=kls.__name__)
    elif kls.__module__ in sys.stdlib_module_names:
        mod = kls.__module__
        url = BUILTIN_URL.format(mod=mod, name=f"{mod}.{kls.__name__}")
        link = linked(url, title=kls.__name__)
    elif kls.__module__.startswith(("PyQt", "PySide")):
        mod = kls.__module__.replace("PySide6.", "").replace("PyQt6.", "")
        url = f"{BASE_URL}{mod}/{kls.__qualname__.replace('.', '/')}.html"
        link = linked(url, title=kls.__name__)
    elif kls.__module__.startswith("prettyqt"):
        link = linked(kls.__qualname__)
    else:
        try:
            dist = metadata.distribution(kls.__module__.split(".")[0])
        except metadata.PackageNotFoundError:
            link = linked(kls.__qualname__)
        else:
            if url := dist.metadata["Home-Page"]:
                link = linked(url, title=kls.__qualname__)
            else:
                link = linked(kls.__qualname__)
    return styled(link, **kwargs)


def label_for_class(klass: type) -> str:
    if klass.__module__.startswith(("PyQt", "PySide")):
        return f"{klass.__module__.split('.')[-1]}.{klass.__name__}"
    elif klass.__module__.startswith("prettyqt."):
        parts = klass.__module__.split(".")
        return f"{parts[1]}.{klass.__name__}"
    return klass.__qualname__


def to_html_list(
    ls: list[str], shorten_after: int | None = None, make_link: bool = False
):
    if not ls:
        return ""
    item_str = "".join(
        f"<li>{linked(i)}</li>" if make_link else f"<li>{i}</li>"
        for i in ls[:shorten_after]
    )
    if shorten_after and len(ls) > shorten_after:
        item_str += "<li>...</li>"
    return f"<ul>{item_str}</ul>"


def format_kwargs(kwargs: dict[str, Any]) -> str:
    if not kwargs:
        return ""
    kw_parts = []
    for k, v in kwargs.items():
        if isinstance(v, type | types.ModuleType | types.MethodType | types.FunctionType):
            name = v.__name__
        else:
            name = repr(v)
        kw_parts.append(f"{k}={name}")
    return ", ".join(kw_parts)


class ConnectionBuilder:
    def __init__(self, objects, *args, **kwargs):
        self.items = set()
        self.connections = []
        self._connect(objects)

    def _connect(self, objects):
        def add_connections(item):
            identifier = self.get_id(item)
            if identifier not in self.items:
                # if item.__module__.startswith(base_module):
                self.items.add(identifier)
                for base in self.get_children(item):
                    self.connections.append((self.get_id(base), identifier))
                    add_connections(base)

        for obj in objects:
            add_connections(obj)

    def get_children(self, item):
        """This should return a list of children for the tree node."""
        return NotImplemented

    def get_id(self, item):
        """This needs to return a unique identifier for an item."""
        return item

    def get_attributes(self, item):
        return None

    def get_title(self, item):
        """This can be overridden for a nicer label."""
        return self.get_id(item)

    def get_graph_connection_text(self):
        items = list(self.items) + [f"{a} --> {b}" for a, b in self.connections]
        return textwrap.indent("\n".join(items), "  ")


if __name__ == "__main__":
    strings = [str(i) for i in range(1000)]
    print(limit_repr.repr(strings))
