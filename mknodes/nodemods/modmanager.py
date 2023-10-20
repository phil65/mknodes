from __future__ import annotations

from mknodes.nodemods import parallax, scrollreveal
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


class ModManager:
    def __init__(self):
        self.mods = []
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

    def get_resources(self) -> resources.Resources:
        req = resources.Resources()
        for mod in self.mods:
            req.merge(mod.get_resources())
        return req

    @property
    def css_classes(self) -> list[str]:
        cls_names = [cls_name for mod in self.mods for cls_name in mod.css_class_names]
        return self._css_classes + cls_names

    @property
    def attr_list_str(self):
        classes = " ".join(self.css_classes)
        return f"{{: .{classes}}}"

    def add_parallax_effect(self, orientation: str = "up"):
        effect = parallax.ParallaxEffect(orientation=orientation)
        self.mods.append(effect)

    def add_scroll_effect(self, origin: str = "left"):
        effect = scrollreveal.ScrollReveal(origin=origin)
        self.mods.append(effect)


if __name__ == "__main__":
    manager = ModManager()
    print(manager.get_resources())