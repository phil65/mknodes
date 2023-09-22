from __future__ import annotations

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import log, reprhelpers, requirements


logger = log.get_logger(__name__)

# https://ruyadorno.com/simple-slider/

JS_URL = "https://rawgit.com/ruyadorno/simple-slider/master/dist/simpleslider.min.js"

HTML = """
<div style="width: 100%; padding-bottom: 25%" data-simple-slider>
{images}
</div>
"""
SCRIPT = r"""
<script>
  window.addEventListener('DOMContentLoaded', function () {
  simpleslider.getSlider();
})
</script>
"""


class MkImageSlideshow(mknode.MkNode):
    """Node to show an Image comparison (using a slider)."""

    ICON = "material/image-multiple"
    REQUIRED_EXTENSIONS = [
        requirements.Extension("attr_list"),
        requirements.Extension("md_in_html"),
    ]
    JS_FILES = [requirements.JSLink(JS_URL)]

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

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            images=self.images,
            _filter_empty=True,
            _filter_false=True,
        )

    def _to_markdown(self) -> str:
        lines = [f'  <img src="{i}"/>' for i in self.images]
        return HTML.format(images="\n".join(lines)) + SCRIPT

    @staticmethod
    def create_example_page(page):
        import mknodes

        images = ["https://picsum.photos/700", "https://picsum.photos/701"]
        node = MkImageSlideshow(images)
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    img = MkImageSlideshow(["https://picsum.photos/200", "https://picsum.photos/201"])
    print(img.get_requirements())
