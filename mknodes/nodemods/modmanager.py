from __future__ import annotations

from mknodes.nodemods import parallax, scrollreveal
from mknodes.utils import log, reprhelpers, resources


logger = log.get_logger(__name__)


class ModManager:
    def __init__(self, mods=None, css_classes: list[str] | None = None):
        self.mods = mods or []
        self._css_classes = css_classes or []

    def __hash__(self):
        return sum([hash(i) for i in self.css_classes])

    def __eq__(self, other):
        """Needed for Mknode comparison."""
        return hash(self) == hash(other)

    def __repr__(self):
        return reprhelpers.get_repr(self, mods=self.mods, css_classes=self._css_classes)

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
    def attr_list_str(self) -> str:
        classes = " ".join(self.css_classes)
        return f"{{: .{classes}}}"

    def add_parallax_effect(
        self,
        orientation: str = "up",
        scale: float = 1.5,
        overflow: bool = False,
        delay: float = 0.6,
        transition: str = "cubic-bezier(0,0,0,1)",
    ):
        """Add a parallax effect to the node.

        Arguments:
            orientation: Orientation of the effect
            scale: Effect scale
            overflow: Overflow
            delay: Effect delay
            transition: transition as CSS string
        """
        effect = parallax.ParallaxEffect(
            orientation=orientation,
            scale=scale,
            overflow=overflow,
            delay=delay,
            transition=transition,
        )
        self.mods.append(effect)

    def add_scroll_effect(
        self,
        origin: str = "left",
        distance: str = "300px",
        easing: str = "ease-in-out",
        reset: bool = True,
        duration: int = 800,
    ):
        """Add a scroll-reveal effect to the node.

        Arguments:
            origin: Origin of the effect
            distance: Distance of the slide effect
            easing: Animation easing
            reset: Whether animation should be reversed when element leaves visible area.
            duration: Effect duration
        """
        effect = scrollreveal.ScrollReveal(
            origin=origin,
            distance=distance,
            easing=easing,
            reset=reset,
            duration=duration,
        )
        self.mods.append(effect)


if __name__ == "__main__":
    manager = ModManager()
    print(manager.get_resources())
