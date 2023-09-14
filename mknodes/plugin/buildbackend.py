from __future__ import annotations

import os
import pathlib

from mknodes.utils import log


logger = log.get_logger(__name__)


class BuildBackend:
    def __init__(
        self,
        path: str | os.PathLike | None = None,
    ):
        self.directory = pathlib.Path(path or ".")
        self.assets_path = pathlib.Path(self.directory) / "assets"
        self.asset_files: dict[str, str | bytes] = {}
        self._files: dict[str, str | bytes] = {}

    def _write_file(self, path: str | os.PathLike, content: str | bytes):
        raise NotImplementedError

    def write_file(self, path: str | os.PathLike, content: str | bytes):
        logger.debug("%s: Writing file to %r", type(self).__name__, str(path))
        self._files[pathlib.Path(path).as_posix()] = content
        self._write_file(path, content)

    def write_files(self, dct: dict[str, str | bytes]):
        """Write a mapping of {filename: file_content} to build directory."""
        for k, v in dct.items():
            self.write_file(k, v)

    def write_assets(self, dct: dict[str, str | bytes]):
        for k, v in dct.items():
            logger.debug("%s: Writing asset to %r", type(self).__name__, str(v))
            self.asset_files[(self.assets_path / k).as_posix()] = v
            self._write_file(self.assets_path / k, v)

    @property
    def css_files(self):
        return [i for i in self.asset_files if i.endswith(".css")]

    @property
    def js_files(self):
        return [i for i in self.asset_files if i.endswith(".js")]


if __name__ == "__main__":
    b = BuildBackend()
