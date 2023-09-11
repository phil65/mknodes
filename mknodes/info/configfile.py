from __future__ import annotations

from abc import ABCMeta
from collections.abc import MutableMapping
import os
import pathlib

from typing import Any

from mknodes.utils import cache, helpers


class ConfigFile(MutableMapping, metaclass=ABCMeta):
    def __init__(self, path: str | os.PathLike | None = None):
        self._data: dict[str, Any] = {}
        self.path = path
        if self.path is None:
            return
        self.path = str(path)
        if helpers.is_url(self.path):
            content = cache.download_and_cache_url(self.path, days=1)
            self.load_config(content.decode())
        else:
            self.load_file(self.path)

    def __getitem__(self, value):
        if isinstance(value, str):
            return self._data.__getitem__(value)
        return self.get_section(value)

    def __setitem__(self, index, value):
        self._data[index] = value

    def __delitem__(self, index):
        del self._data[index]

    def __repr__(self):
        return f"{type(self).__name__}({self.path!r})"

    def __bool__(self):
        return bool(self._data or self.path)

    def __iter__(self):
        return iter(self._data.keys())

    def __len__(self):
        return len(self._data)

    def get_section(self, *sections: str, keep_path: bool = False) -> Any:
        # sourcery skip: merge-duplicate-blocks
        """Try to get data[sections[0]][sections[1]]...

        If Key path does not exist, return None.

        Arguments:
            sections: Sections to dig into
            keep_path: Return result with original nesting
        """
        return helpers.get_nested_json(self._data)

    def get_section_text(
        self,
        *sections: str,
        keep_path: bool = False,
        multiline_strings: bool = False,
    ) -> str:
        """Try to get data[sections[0]][sections[1]]... as text.

        If Key path does not exist, return empty string.

        Arguments:
            sections: Sections to dig into
            keep_path: Return result with original nesting
            multiline_strings: Format as multiline
        """
        if not sections:
            raise ValueError(sections)
        section = self.get_section(*sections, keep_path=keep_path)
        return "" if section is None else self._dump(section)

    def load_config(self, data: str):
        self._data = self._load(data)

    def dump_config(self) -> str:
        return self._dump(self._data)

    def load_file(self, path: str | os.PathLike):
        text = pathlib.Path(path).read_text(encoding="utf-8")
        self.load_config(text)

    @classmethod
    def _dump(cls, data: dict) -> str:
        raise NotImplementedError

    @classmethod
    def _load(cls, data: str) -> dict | list:
        raise NotImplementedError


if __name__ == "__main__":
    from mknodes.info import tomlfile

    info = tomlfile.TomlFile("pyproject.toml")
    text = info.get_section_text("tool", "hatch", keep_path=True)
    print(text)
