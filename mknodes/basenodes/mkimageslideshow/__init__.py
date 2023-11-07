from __future__ import annotations

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import log, resources, xmlhelpers as xml


logger = log.get_logger(__name__)

# https://ruyadorno.com/simple-slider/

JS_URL = "https://rawgit.com/ruyadorno/simple-slider/master/dist/simpleslider.min.js"

SCRIPT = """\
window.addEventListener('DOMContentLoaded', function () {
  simpleslider.getSlider();
})
"""


class MkImageSlideshow(mknode.MkNode):
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
        super().__init__(**kwargs)
        self.images = images

    def get_element(self) -> xml.Div:
        attrs = {"data-simple-slider": ""}
        root = xml.Div(style="width: 100%; padding-bottom: 25%", parent=None, **attrs)
        for img in self.images:
            xml.Img(src=img, parent=root)
        return root

    def _to_markdown(self) -> str:
        root = self.get_element()
        return root.to_string()

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        images = ["https://picsum.photos/700", "https://picsum.photos/701"]
        node = MkImageSlideshow(images)
        page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    img = MkImageSlideshow(["https://picsum.photos/200", "https://picsum.photos/201"])
