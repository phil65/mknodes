from __future__ import annotations

import os
import pathlib
import tomllib

from typing import Any

import tomli_w

from mknodes.utils import cache, helpers


class TomlFile:
    def __init__(self, path: str | os.PathLike):
        self.path = str(path)
        path = pathlib.Path(path)
        if helpers.is_url(self.path):
            content = cache.download_and_cache_url(self.path, days=1)
            self._data = tomllib.loads(content.decode())
        else:
            text = path.read_text(encoding="utf-8")
            self._data = tomllib.loads(text)

    def __getitem__(self, value):
        if isinstance(value, str):
            return self._data.__getitem__(value)
        return self.get_section(value)

    def __getattr__(self, item: str) -> Any:
        return getattr(self._data, item.replace("-", "_"))

    def __dir__(self) -> Any:
        additional = [k.replace("-", "_") for k in self._data]
        return list(super().__dir__()) + additional

    def __repr__(self):
        return f"{type(self).__name__}({self.path})"

    def get_section(self, *sections) -> Any:
        """Try to get data[sections[0]][sections[1]]...

        If Key path does not exist, return None.

        Arguments:
            sections: Sections to dig into
        """
        section = self._data
        for i in sections:
            if child := section.get(i):
                section = child
            else:
                return None
        return section

    def get_section_text(self, *sections, multiline_strings: bool = False) -> str:
        """Try to get data[sections[0]][sections[1]]... as text.

        If Key path does not exist, return empty string.

        Arguments:
            sections: Sections to dig into
            multiline_strings: Format as multiline
        """
        section = self.get_section(*sections)
        return (
            ""
            if section is None
            else tomli_w.dumps(section, multiline_strings=multiline_strings)
        )


if __name__ == "__main__":
    info = TomlFile("pyproject.toml")
    print(info.get_section_text("tool", "hatch"))
