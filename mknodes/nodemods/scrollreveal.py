from __future__ import annotations

import dataclasses

from mknodes.nodemods import modhelpers
from mknodes.utils import helpers, resources


SCROLLREVEAL_LINK = (
    "https://cdn.jsdelivr.net/npm/scrollreveal@3.4.0/dist/scrollreveal.min.js"
)
JQUERY_LINK = "https://code.jquery.com/jquery-2.2.4.min.js"

SCRIPT = """\
window.sr = ScrollReveal();

// Add class to <html> if ScrollReveal is supported
// Note: only works in version 3
if (sr.isSupported()) {
document.documentElement.classList.add('sr');
}
"""


SCRIPT_2 = """\
$(window).load(function(){

  window.sr = ScrollReveal();
  sr.reveal('.%s', %s);
});

"""

#   window.sr = ScrollReveal();
#   sr.reveal('.%s', {
#       origin: 'left',
#       distance: '300px',
#       easing: 'ease-in-out',
#       reset: true,
#       duration: 800,
#     });
# });


@dataclasses.dataclass(frozen=True)
class ScrollReveal:
    origin: str = "left"
    distance: str = "300px"
    easing: str = "ease-in-out"
    reset: bool = True
    duration: int = 800

    def get_resources(self):
        jquery_res = resources.JSFile(JQUERY_LINK, is_library=True)
        scrollreveal_res = resources.JSFile(SCROLLREVEAL_LINK, is_library=True)
        res1 = resources.JSText(SCRIPT, "scrollreveal.js")
        dct = dataclasses.asdict(self)
        js_map = modhelpers.format_js_map(dct)
        script_text = SCRIPT_2 % (self.css_class_names[-1], js_map)
        res2 = resources.JSText(script_text, "script.js")
        return resources.Resources(
            js=[
                jquery_res,
                scrollreveal_res,
                res1,
                res2,
            ],
        )

    @property
    def css_class_names(self):
        return ["sr", f"scrollreveal_{helpers.get_hash(self)}"]


if __name__ == "__main__":
    effect = ScrollReveal(origin="right")
    print(effect.get_resources().js[-1])
