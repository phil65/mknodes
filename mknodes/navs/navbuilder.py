from __future__ import annotations

from collections.abc import Iterable, Mapping
import dataclasses
import os


class NavBuilder:
    """An object representing MkDocs navigation.

    Consists of files under nested
    sequences of titles, which are treated like paths.
    """

    def __init__(self):
        self._data = {}

    def __setitem__(self, keys: str | tuple[str, ...], value: str):
        """Add a link to a file into the nav, under the sequence of titles.

        For example, writing `nav["Foo", "Bar"] = "foo/bar.md"` would mean creating a nav:
        `{"Foo": {"Bar": "foo/bar.md"}}`.

        Then, writing `nav["Foo", "Another"] = "test.md"` would merge with the existing
        sections where possible:
        `{"Foo": {"Bar": "foo/bar.md", "Another": "test.md"}}`.
        """
        if isinstance(keys, str):
            keys = (keys,)
        cur = self._data
        if not keys:
            msg = f"The navigation path must not be empty (got {keys!r})"
            raise ValueError(msg)
        for key in keys:
            if not isinstance(key, str):
                msg = f"The navigation path must consist of strings, got {type(key)}"
                raise TypeError(msg)
            if not key:
                msg = f"The navigation name parts must not be empty (got {keys!r})"
                raise ValueError(msg)
            cur = cur.setdefault(key, {})
        cur[None] = os.fspath(value)

    @dataclasses.dataclass
    class Item:
        level: int
        title: str
        filename: str | None

    def items(self) -> Iterable[Item]:
        return self._items(self._data, 0)

    @classmethod
    def _items(cls, data: Mapping, level: int) -> Iterable[Item]:
        for key, value in data.items():
            if key is not None:
                yield cls.Item(level=level, title=key, filename=value.get(None))
                yield from cls._items(value, level + 1)

    _markdown_escape_chars = tuple("!#()*+-[\\]_`{}")

    def build_literate_nav(self, indentation: int | str = "") -> Iterable[str]:
        """Convert data to a literate-nav formatted markdown list.

        Arguments:
            indentation: Initial indentation
        """
        if isinstance(indentation, int):
            indentation = " " * indentation
        for item in self.items():
            line = item.title
            if line.startswith(self._markdown_escape_chars):
                line = "\\" + line
            if item.filename is not None:
                line = f"[{line}]({item.filename})"
            yield indentation + "    " * item.level + "* " + line + "\n"
