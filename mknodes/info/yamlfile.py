from __future__ import annotations

import os

import upath

from mknodes.info import configfile
from mknodes.utils import log, mergehelpers, yamlhelpers


logger = log.get_logger(__name__)


class YamlFile(configfile.ConfigFile):
    def __init__(
        self,
        path: str | os.PathLike | None = None,
        mode: yamlhelpers.LoaderStr = "unsafe",
        resolve_inherit_tag: bool = False,
    ):
        super().__init__(path)
        if resolve_inherit_tag:
            self.resolve_inherit_tag(mode)

    def resolve_inherit_tag(
        self,
        mode: yamlhelpers.LoaderStr = "unsafe",
    ):
        """Resolve INHERIT key-value pair for this YAML file.

        If this YAML file contains a key-value pair like "INHERIT: path_to_config.yml",
        this method will resolve that tag by using the config at given path as the
        "parent config".

        Also supports a list of files for INHERIT.

        Arguments:
            mode: The Yaml loader type
        """
        if not self.path:
            msg = "Config file needs file path (INHERIT path is relative to file path)"
            raise ValueError(msg)
        abspath = upath.UPath(self.path).absolute()
        if "INHERIT" not in self._data:
            return
        file_path = self._data.pop("INHERIT")
        file_paths = [file_path] if isinstance(file_path, str) else file_path
        for path in file_paths:
            parent_cfg = abspath.parent / path
            logger.debug("Loading inherited configuration file: %s", parent_cfg)
            text = parent_cfg.read_text()
            parent = yamlhelpers.load_yaml(text, mode)
            self._data = mergehelpers.merge_dicts(parent, self._data)

    @classmethod
    def _dump(cls, data: dict) -> str:
        return yamlhelpers.dump_yaml(data)

    @classmethod
    def _load(cls, data: str, mode: yamlhelpers.LoaderStr = "unsafe") -> dict | list:
        return yamlhelpers.load_yaml(data, mode)


if __name__ == "__main__":
    info = YamlFile(".pre-commit-config.yaml")
    print(info)
