from __future__ import annotations

import json
import os
import pathlib

from typing import Any

from mknodes.utils import cache, helpers


class ConfigFile:
    def __init__(self, path: str | os.PathLike):
        self.path = str(path)
        path = pathlib.Path(path)
        if helpers.is_url(self.path):
            content = cache.download_and_cache_url(self.path, days=1)
            self.load_config(content.decode())
        else:
            self.load_file(path)

    def __getitem__(self, value):
        if isinstance(value, str):
            return self._data.__getitem__(value)
        return self.get_section(value)

    def __repr__(self):
        return f"{type(self).__name__}({self.path!r})"

    def get_section(self, *sections: str, keep_path: bool = False) -> Any:
        """Try to get data[sections[0]][sections[1]]...

        If Key path does not exist, return None.

        Arguments:
            sections: Sections to dig into
            keep_path: Return result with original nesting
        """
        section = self._data
        for i in sections:
            if child := section.get(i):
                section = child
            else:
                return None
        if not keep_path:
            return section
        result: dict[str, dict] = {}
        new = result
        for sect in sections:
            result[sect] = section if sect == sections[-1] else {}
            result = result[sect]
        return new

    def get_section_text(
        self,
        *sections,
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
        return "" if section is None else json.dumps(section)

    def load_config(self, data: str):
        self._data: dict = self._load(data)

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
    info = ConfigFile("pyproject.toml")
    text = info.get_section_text("tool", "hatch", keep_path=True)
    print(text)
