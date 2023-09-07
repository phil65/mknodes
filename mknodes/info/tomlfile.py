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
            content = cache.download_and_cache_url(self.path, days=1).decode()
            self._data = tomllib.loads(content)
        else:
            self._data = tomllib.loads(path.read_text(encoding="utf-8"))

    def __getitem__(self, value):
        return self._data.__getitem__(value)

    def __repr__(self):
        return f"{type(self).__name__}({self.path})"

    def get_section(self, *sections) -> Any:
        section = self._data
        for i in sections:
            if child := section.get(i):
                section = child
            else:
                return None
        return section

    def get_section_text(self, *sections) -> str:
        section = self.get_section(*sections)
        return "" if section is None else tomli_w.dumps(section)


if __name__ == "__main__":
    info = TomlFile("pyproject.toml")
    print(info.get_section_text("tool", "hatch"))
