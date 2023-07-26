from __future__ import annotations

import logging

from mknodes import mkcontainer


logger = logging.getLogger(__name__)


class MkAnnotations(mkcontainer.MkContainer):
    """Node containing a list of annotations."""

    def __len__(self):
        return len(self.items)

    @staticmethod
    def examples():  # 1
        yield dict(items=["Item 1"])

    def _to_markdown(self) -> str:
        if not self.items:
            return ""
        result = []
        for i, item in enumerate(self.items, start=1):
            lines = str(item).split("\n")
            space = (3 - len(str(i))) * " "
            result.append(f"{i}.{space}{lines[0]}")
            result.extend(f"    {i}" for i in lines[1:])
        return "\n".join(result) + "\n"


if __name__ == "__main__":
    section = MkAnnotations(["abcde\nfghi"] * 10, header="Header")
    print(section.to_markdown())
