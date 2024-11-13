from __future__ import annotations

from typing import TYPE_CHECKING, Any

import yamling

from mknodes.utils import superdict


if TYPE_CHECKING:
    import os


class ConfigFile(superdict.SuperDict):
    filetype: str | None = None

    def __init__(self, path: str | os.PathLike[str] | None = None):
        """Constructor.

        Args:
            path: Path to the config file (supports fsspec protocol URLs)
        """
        super().__init__()
        self.path = str(path or "")
        if self.path:
            self.load_file(self.path)

    def __repr__(self):
        return f"{type(self).__name__}({self.path!r})"

    def __bool__(self):
        return bool(self._data or self.path)

    def get_section_text(
        self,
        *sections: str,
        keep_path: bool = False,
    ) -> str:
        """Try to get data from given path as text.

        If Key path does not exist, return empty string.

        Args:
            sections: Sections to dig into
            keep_path: Return result with original nesting
        """
        if not sections:
            raise ValueError(sections)
        section = self.get_section(*sections, keep_path=keep_path)
        return "" if section is None else yamling.dump(section, mode=self.filetype)  # type: ignore[arg-type]

    def dump_config(self) -> str:
        """Dump to string with dumper of given file type."""
        return yamling.dump(self._data, mode=self.filetype)  # type: ignore[arg-type]

    def load_file(
        self,
        path: str | os.PathLike[str],
        **storage_options: Any,
    ):
        """Load a file with loader of given file type.

        Args:
            path: Path to the config file (also supports fsspec protocol URLs)
            storage_options: Options for fsspec backend
        """
        self._data = yamling.load_file(path, storage_options=storage_options or {})


class TomlFile(ConfigFile):
    filetype = "toml"


class YamlFile(ConfigFile):
    filetype = "yaml"

    def load_file(
        self,
        path: str | os.PathLike[str],
        **storage_options: Any,
    ):
        """Load a file with loader of given file type.

        Args:
            path: Path to the config file (also supports fsspec protocol URLs)
            storage_options: Options for fsspec backend
        """
        self._data = yamling.load_yaml_file(
            path,
            storage_options=storage_options or {},
            resolve_inherit=True,
        )
        # type: ignore[arg-type]


if __name__ == "__main__":
    info = TomlFile("github://phil65:mknodes@main/pyproject.toml")
    text = info.get_section_text("tool", "hatch", keep_path=True)
    print(text)
