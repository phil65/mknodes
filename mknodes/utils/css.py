from __future__ import annotations

from collections.abc import Mapping


class CSS:
    def __init__(self, obj: Mapping):
        self.obj = obj
        self._data: dict[str, list] = {}
        self._parse(obj)

    def __repr__(self):
        return self.to_string()

    def to_string(self) -> str:
        string = ""
        for key, value in sorted(self._data.items()):
            if self._data[key]:
                string += key[1:] + " {\n" + "".join(value) + "}\n\n"
        return string

    def _parse(self, obj, selector: str = ""):
        for key, value in obj.items():
            if hasattr(value, "items"):
                rule = selector + " " + key
                self._data[rule] = []
                self._parse(value, rule)

            else:
                prop = self._data[selector]
                prop.append(f"\t{key}: {value};\n")


if __name__ == "__main__":
    css = CSS({".test": {"color": "red"}})
    print(css)
