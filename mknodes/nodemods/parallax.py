from __future__ import annotations

import dataclasses

from mknodes.utils import helpers, resources


SCRIPT = """
var image = document.getElementsByClassName({class_name});
new simpleParallax(image, {
    orientation: 'right',
    scale: 1.5,
    overflow: true,
    delay: .6,
    transition: 'cubic-bezier(0,0,0,1)',
    maxTransition: 60
});
"""

LIB = "https://cdn.jsdelivr.net/npm/simple-parallax-js@5.5.1/dist/simpleParallax.min.js"

file = resources.JSFile(LIB)
script = resources.JSText(SCRIPT, filename="parallax.js")


@dataclasses.dataclass(frozen=True)
class ParallaxEffect:
    orientation: str = "up"
    scale: float = 1.2
    overflow: bool = False

    def get_resources(self):
        return resources.Resources(js=[file, script])

    @property
    def css_class_name(self):
        return f"parallax_{helpers.get_hash(self)}"


if __name__ == "__main__":
    effect = ParallaxEffect(orientation="down")
    print(effect.css_class_name)
