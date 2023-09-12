from __future__ import annotations

from abc import ABCMeta
from collections.abc import MutableMapping
from typing import Any


class SuperDict(MutableMapping, metaclass=ABCMeta):
    def __init__(self, data: dict | None = None, **kwargs):
        self._data: dict[str, Any] = data or {}
        self._data |= kwargs

    def __getitem__(self, value):
        if isinstance(value, str):
            return self._data.__getitem__(value)
        return self.get_section(value)

    def __setitem__(self, index, value):
        self._data[index] = value

    def __delitem__(self, index):
        del self._data[index]

    def __bool__(self):
        return bool(self._data)

    def __iter__(self):
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
            return section
        result: dict[str, dict] = {}
        new = result
        for sect in sections:
            result[sect] = section if sect == sections[-1] else {}
            result = result[sect]
        return new


if __name__ == "__main__":
    dct = SuperDict(a=dict(b="c"))
    text = dct.get_section("a", "b", keep_path=False)
    print(text)
