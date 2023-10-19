from __future__ import annotations

from mknodes.nodemods import parallax
from mknodes.utils import log


logger = log.get_logger(__name__)


class ModManager:
    def __init__(self):
        self.mods: list[parallax.ParallaxEffect] = []
        self._css_classes = []

    def __hash__(self):
        return sum([hash(i) for i in self.css_classes])

    def __eq__(self, other):
        """Needed for Mknode comparison."""
        return hash(self) == hash(other)

    def append(self, other):
        if isinstance(other, str):
            self._css_classes.append(other)
        else:
            self.mods.append(other)

    def get_resources(self):
        return None

    @property
    def css_classes(self):
        return self._css_classes + [mod.css_class_name for mod in self.mods]

    def add_parallax(self, orientation: str = "up"):
        effect = parallax.ParallaxEffect(orientation=orientation)
        self.mods.append(effect)


if __name__ == "__main__":
    manager = ModManager()
    manager.add_parallax()
    print(manager.css_classes)
