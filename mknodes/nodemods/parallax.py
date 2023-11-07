from __future__ import annotations

import dataclasses

from jinjarope import envglobals

from mknodes.utils import helpers, resources


SCRIPT = """\
var image = document.getElementsByClassName('%s');
new simpleParallax(image, %s);
"""

LIB = "https://cdn.jsdelivr.net/npm/simple-parallax-js@5.5.1/dist/simpleParallax.min.js"


@dataclasses.dataclass(frozen=True)
class ParallaxEffect:
    orientation: str = "up"
    scale: float = 1.5
    overflow: bool = False
    delay: float = 0.6
    transition: str = "cubic-bezier(0,0,0,1)"
    # max_transition: int = 100

    def get_resources(self):
        file = resources.JSFile(LIB, is_library=True)
        dct = dataclasses.asdict(self)
        js_map = envglobals.format_js_map(dct)
        text = SCRIPT % (self.css_class_names[0], js_map)
        script = resources.JSText(text, filename="parallax.js")
        return resources.Resources(js=[file, script])

    @property
    def css_class_names(self):
        return [f"parallax_{helpers.get_hash(self)}"]


if __name__ == "__main__":
    effect = ParallaxEffect(orientation="down")
    print(effect.css_class_names)
