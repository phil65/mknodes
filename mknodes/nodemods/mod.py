from __future__ import annotations

from mknodes.utils import log, resources


logger = log.get_logger(__name__)


class Mod:
    def get_resources(self) -> resources.Resources:
        return resources.Resources()

    @property
    def css_class_names(self) -> list[str]:
        return []


if __name__ == "__main__":
    manager = Mod()
