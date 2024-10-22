from __future__ import annotations

from abc import ABCMeta
from collections.abc import Iterator, MutableMapping
from typing import TYPE_CHECKING, Any, Literal, Self, TypeVar

from jinjarope import serializefilters

from mknodes.utils import pathhelpers, reprhelpers


if TYPE_CHECKING:
    import os


MarkupTypeStr = Literal["yaml", "json", "toml"]


V = TypeVar("V")


class SuperDict(MutableMapping[str, V], metaclass=ABCMeta):
    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any):
        self._data: dict[str, V] = data or {}
        self._data |= kwargs

    def __getitem__(self, value: str | tuple[str, ...]) -> V:
        if isinstance(value, str):
            return self._data.__getitem__(value)
        return self.get_section(*value)

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

    def __repr__(self):
        return reprhelpers.get_repr(self, data=dict(self._data))

    def rename_key(self, old: str, new: str) -> Self:
        """Rename a key of the dict while preserving key order.

        Arguments:
            old: the old key
            new: the new key
        """
        dct = {new if k == old else k: v for k, v in self.items()}
        self.update(dct)
        return self

    def get_section(self, *sections: str, keep_path: bool = False) -> Any:
        """Try to get data with given section path from a dict-list structure.

        If a list is encountered, treat it like a list of
        {"identifier", {subdict}} items, as used in MkDocs config for
        plugins & extensions.
        If Key path does not exist, return None.

        Arguments:
            sections: Sections to dig into
            keep_path: Return result with original nesting
        """
        result = serializefilters.dig(self._data, *sections, keep_path=keep_path)
        return SuperDict(result) if isinstance(result, dict) else result

    def serialize(self, mode: MarkupTypeStr) -> str:  # type: ignore[return]
        return serializefilters.serialize(self._data, mode)

    def write(self, path: str | os.PathLike[str], mode: MarkupTypeStr):
        text = self.serialize(mode)
        pathhelpers.write_file(text, path)


if __name__ == "__main__":
    dct = SuperDict(a=dict(b="c"))  # type: ignore[var-annotated]
    text = dct.get_section("a", "b", keep_path=False)
    print(text)
