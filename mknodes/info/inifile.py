from __future__ import annotations

import configparser
import io

from mknodes.info import configfile


config = configparser.ConfigParser()


class IniFile(configfile.ConfigFile):
    @classmethod
    def _dump(cls, data: dict) -> str:
        config.read_dict(data)
        file = io.StringIO()
        with file as fp:
            config.write(fp)
            return file.getvalue()

    @classmethod
    def _load(cls, data: str) -> dict:
        config.read_string(data)
        return {s: dict(config.items(s)) for s in config.sections()}


if __name__ == "__main__":
    test = """
    [Section 1]
    option = value

    [  Section 2  ]
    another = val
    """
    info = IniFile()
    dct = info._load(test)
    print(info._dump(dct))
