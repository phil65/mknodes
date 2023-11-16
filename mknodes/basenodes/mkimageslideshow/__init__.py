from __future__ import annotations

from typing import Any

from mknodes.templatenodes import mktemplate
from mknodes.utils import log, resources


logger = log.get_logger(__name__)

# https://ruyadorno.com/simple-slider/

JS_URL = "https://rawgit.com/ruyadorno/simple-slider/master/dist/simpleslider.min.js"

SCRIPT = """\
window.addEventListener('DOMContentLoaded', function () {
  simpleslider.getSlider();
})
"""


class MkImageSlideshow(mktemplate.MkTemplate):
    """Node to show an Image slideshow (in autoplay mode)."""

    ICON = "material/image-multiple"
    JS_FILES = [resources.JSFile(JS_URL), resources.JSText(SCRIPT, "slideshow.js")]

    def __init__(
        self,
        images: list[str],
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            images: A list of image URLs to use for the slideshow
            kwargs: Keyword arguments passed to parent
        """
        super().__init__("output/html/template", **kwargs)
        self.images = images


if __name__ == "__main__":
    img = MkImageSlideshow(["https://picsum.photos/200", "https://picsum.photos/201"])
    print(img)
