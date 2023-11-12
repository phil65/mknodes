from __future__ import annotations

from typing import Any

from mknodes.templatenodes import mktemplate
from mknodes.utils import resources


JS_URL = "https://unpkg.com/img-comparison-slider@7/dist/index.js"

CSS_URL = "https://unpkg.com/img-comparison-slider@7/dist/styles.css"


class MkImageCompare(mktemplate.MkTemplate):
    """Node to show an Image comparison (using a slider)."""

    ICON = "material/image-off"
    JS_FILES = [resources.JSFile(JS_URL, defer=True)]
    CSS = [resources.CSSFile(CSS_URL)]

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
        super().__init__("output/html/template", **kwargs)
        self.before_image = before_image
        self.after_image = after_image

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkImageCompare(
            before_image="https://picsum.photos/700",
            after_image="https://picsum.photos/701",
        )
        page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    img = MkImageCompare("a", "b")
    print(img)
