from __future__ import annotations

from abc import ABCMeta
from collections.abc import Iterator, MutableMapping
import os

from typing import Any, Literal, TypeVar

from mknodes.utils import pathhelpers


MarkupTypeStr = Literal["yaml", "json", "toml"]


V = TypeVar("V")


class SuperDict(MutableMapping[str, V], metaclass=ABCMeta):
    def __init__(self, data: dict | None = None, **kwargs):
        self._data: dict[str, V] = data or {}
        self._data |= kwargs

    def __getitem__(self, value: str) -> V:
        if isinstance(value, str):
            return self._data.__getitem__(value)
        return self.get_section(value)

    def __setitem__(self, index: str, value: V):
        self._data[index] = value

    def __delitem__(self, index: str):
        del self._data[index]

    def __bool__(self):
        return bool(self._data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data.keys())

    def __len__(self):
        return len(self._data)

    def get_section(self, *sections: str, keep_path: bool = False) -> Any:
        """Try to get data[sections[0]][sections[1]]...

        If Key path does not exist, return None.

        Arguments:
            sections: Sections to dig into
            keep_path: Return result with original nesting
        """
        section = self._data
        for i in sections:
            if isinstance(section, dict):
                if child := section.get(i):
                    section = child
                else:
                    return None
            else:
                for idx in section:
                    if i in idx and isinstance(idx, dict):
                        section = idx[i]
                        break
                    if isinstance(idx, str) and idx == i:
                        section = idx
                        break
                else:
                    return None
        if not keep_path:
            return SuperDict(section) if isinstance(section, dict) else section
        result: dict[str, dict] = {}
        new = result
        for sect in sections:
            result[sect] = section if sect == sections[-1] else {}
            result = result[sect]
        return SuperDict(new) if isinstance(new, dict) else new

    def serialize(self, mode: MarkupTypeStr | None):
        match mode:
            case None | "yaml":
                from mknodes.utils import yamlhelpers

                return yamlhelpers.dump_yaml(self._data)
            case "json":
                import json

                return json.dumps(self._data, indent=4)
            case "toml" if isinstance(self._data, dict):
                import tomli_w

                return tomli_w.dumps(self._data)
            case _:
                raise TypeError(mode)

    def write(self, path: str | os.PathLike, mode: MarkupTypeStr | None = None):
        text = self.serialize(mode)
        pathhelpers.write_file(text, path)


if __name__ == "__main__":
    dct = SuperDict(a=dict(b="c"))  # type: ignore[var-annotated]
    text = dct.get_section("a", "b", keep_path=False)
    print(text)
