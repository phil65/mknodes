from __future__ import annotations

from mknodes.info import configfile
from mknodes.utils import yamlhelpers


class YamlFile(configfile.ConfigFile):
    @classmethod
    def _dump(cls, data: dict) -> str:
        return yamlhelpers.dump_yaml(data)

    @classmethod
    def _load(cls, data: str) -> dict | list:
        return yamlhelpers.load_yaml(data)


if __name__ == "__main__":
    info = YamlFile(".pre-commit-config.yaml")
    print(info)
