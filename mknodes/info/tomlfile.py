from __future__ import annotations

from mknodes.info import configfile


class TomlFile(configfile.ConfigFile):
    filetype = "toml"


if __name__ == "__main__":
    info = TomlFile("pyproject.toml")
    text = info.get_section_text("tool", "hatch", keep_path=True)
    print(text)
