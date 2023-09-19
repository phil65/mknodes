from __future__ import annotations

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import log, reprhelpers, requirements


logger = log.get_logger(__name__)


JS_URL = "https://unpkg.com/img-comparison-slider@7/dist/index.js"

CSS_URL = "https://unpkg.com/img-comparison-slider@7/dist/styles.css"

HTML = """
<img-comparison-slider>
  <img slot="first" src="{before}" />
  <img slot="second" src="{after}" />
</img-comparison-slider>
"""


class MkImageCompare(mknode.MkNode):
    """Node to show an Image comparison (using a slider)."""

    ICON = "material/image-off"
    REQUIRED_EXTENSIONS = [
        requirements.Extension("attr_list"),
        requirements.Extension("md_in_html"),
    ]
    JS_FILES = [requirements.JSLink(JS_URL, defer=True)]
    CSS = [requirements.CSSLink(CSS_URL)]

    def __init__(
        self,
        before_image: str,
        after_image: str,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            before_image: Image shown with slider to the right
            after_image: Image shown with slider to the left
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.before_image = before_image
        self.after_image = after_image

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            _filter_empty=True,
            _filter_false=True,
        )

    def _to_markdown(self) -> str:
        return HTML.format(
            before=self.before_image,
            after=self.after_image,
        )

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkImageCompare(
            before_image="https://picsum.photos/700",
            after_image="https://picsum.photos/701",
        )
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    img = MkImageCompare("a", "b")
    print(img.get_requirements())
