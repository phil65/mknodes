from __future__ import annotations

import dataclasses
import tomllib

from mknodes import paths
from mknodes.info import folderinfo
from mknodes.utils import pathhelpers


@dataclasses.dataclass
class Tool:
    identifier: str
    title: str
    url: str
    description: str
    logo: str | None = None
    setup_cmd: str | None = None
    config_syntax: str | None = None
    pre_commit_repo: str | None = None
    configs: list[dict] = dataclasses.field(default_factory=list)
    cfg: dict = dataclasses.field(default_factory=dict)

    def is_used(self, folder: folderinfo.FolderInfo) -> bool:
        """Return whether tool is used for given directory.

        Arguments:
            folder: Folder to check. Defaults to current working directory.
        """
        for cfg in self.configs:
            if cfg["type"] == "pyproject" and folder.pyproject.tool.get(cfg["section"]):
                self.cfg = cfg
                self.cfg["syntax"] = "toml"
                self.cfg["content"] = self.get_config(folder)
                return True
            if cfg["type"] in {"inifile", "yamlfile", "tomlfile", "jsonfile"}:
                path = pathhelpers.find_cfg_for_folder(cfg["filename"], folder.path)
                if bool(path):
                    self.cfg = cfg
                    self.cfg["syntax"] = cfg["type"].replace("file", "")
                    self.cfg["content"] = self.get_config(folder)
                    return True
        return False

    def get_config(self, folder: folderinfo.FolderInfo) -> str | None:
        """Return config for given tool.

        Arguments:
            folder: Folder to get config from. Defaults to current working directory.
        """
        for cfg in self.configs:
            if cfg["type"] == "pyproject" and folder.pyproject.tool.get(cfg["section"]):
                dct = folder.pyproject.tool.get_section(cfg["section"])
                return dct.serialize("toml")
            if cfg["type"] in {"inifile", "yamlfile", "tomlfile", "jsonfile"}:  # noqa: SIM102
                if p := pathhelpers.find_cfg_for_folder(cfg["filename"], folder.path):
                    return p.read_text(encoding="utf-8")
        return None

    @classmethod
    def from_file(cls, path):
        txt = path.read_text(encoding="utf-8")
        dct = tomllib.loads(txt)
        return cls(**dct)


def get_tools_for_folder(folder) -> list[Tool]:
    tools = []
    for file in (paths.RESOURCES / "toolfiles").iterdir():
        tool = Tool.from_file(file)
        if tool.is_used(folder):
            tools.append(tool)
    return tools


if __name__ == "__main__":
    fi = folderinfo.FolderInfo()
    tools = get_tools_for_folder(fi)
    print(tools)
