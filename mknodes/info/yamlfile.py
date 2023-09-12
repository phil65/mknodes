from __future__ import annotations

import os
import pathlib

from mknodes.info import configfile
from mknodes.utils import log, mergehelpers, yamlhelpers


logger = log.get_logger(__name__)


class YamlFile(configfile.ConfigFile):
    def __init__(
        self,
        path: str | os.PathLike | None = None,
        mode: str = "unsafe",
        inherit_from: str | os.PathLike | None = None,
    ):
        super().__init__(path)
        if inherit_from:
            self.resolve_inherit_tag(inherit_from, mode)

    def resolve_inherit_tag(self, parent_path: str | os.PathLike, mode: str = "unsafe"):
        if "INHERIT" not in self._data:
            return
        relpath = self._data.pop("INHERIT")
        abspath = pathlib.Path(parent_path).absolute()
        if not abspath.exists():
            msg = f"Inherited config file '{relpath}' does not exist at '{abspath}'."
            raise FileNotFoundError(msg)
        logger.debug("Loading inherited configuration file: %s", abspath)
        parent_cfg = abspath.parent / relpath
        with parent_cfg.open("rb") as fd:
            text = fd.read().decode()
            parent = yamlhelpers.load_yaml(text, mode)
        # print(parent, self._data)
        self._data = mergehelpers.merge_dicts(parent, self._data)

    @classmethod
    def _dump(cls, data: dict) -> str:
        return yamlhelpers.dump_yaml(data)

    @classmethod
    def _load(cls, data: str, mode: str = "unsafe") -> dict | list:
        return yamlhelpers.load_yaml(data, mode)


if __name__ == "__main__":
    info = YamlFile(".pre-commit-config.yaml")
    print(info)
