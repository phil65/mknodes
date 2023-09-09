from __future__ import annotations

import json

from mknodes.info import configfile


class JsonFile(configfile.ConfigFile):
    @classmethod
    def _dump(cls, data: dict) -> str:
        return json.dumps(data)

    @classmethod
    def _load(cls, data: str) -> dict | list:
        return json.loads(data)


if __name__ == "__main__":
    info = JsonFile("pyproject.toml")
    text = info.get_section_text("tool", "hatch", keep_path=True)
    print(text)
