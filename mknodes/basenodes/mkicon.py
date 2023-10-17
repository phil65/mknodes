from __future__ import annotations

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import icons, log, reprhelpers


logger = log.get_logger(__name__)


class MkIcon(mknode.MkNode):
    """Pyconify-based Icon."""

    ICON = "material/image"

    def __init__(
        self,
        icon_name: str,
        *,
        color: str | None = None,
        height: str | int | None = None,
        width: str | int | None = None,
        flip: icons.Flip | None = None,
        rotate: icons.Rotation | None = None,
        box: bool | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            icon_name: Icon name
            color: Icon color. Replaces currentColor with specific color, resulting in
                   icon with hardcoded palette.
            height: Icon height. If only one dimension is specified, such as height, other
                    dimension will be automatically set to match it.
            width: Icon width. If only one dimension is specified, such as height, other
                   dimension will be automatically set to match it.
            flip: Flip icon.
            rotate: Rotate icon. If an int is provided, it is assumed to be in degrees.
            box: Adds an empty rectangle to SVG that matches the icon's viewBox.
                 It is needed when importing SVG to various UI design tools that ignore
                 viewBox. Those tools, such as Sketch, create layer groups that
                 automatically resize to fit content. Icons usually have empty pixels
                 around icon, so such software crops those empty pixels and icon's
                 group ends up being smaller than actual icon, making it harder to
                 align it in design.
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.icon_name = icon_name
        self.color = color
        self.height = height
        self.width = width
        self.flip = flip
        self.rotate = rotate
        self.box = box

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            icon_name=self.icon_name,
            color=self.color,
            height=self.height,
            width=self.width,
            flip=self.flip,
            rotate=self.rotate,
            box=self.box,
            _filter_empty=True,
            _filter_false=True,
        )

    def _to_markdown(self) -> str:
        return icons.get_icon_svg(
            self.icon_name,
            color=self.color,
            height=self.height,
            width=self.width,
            flip=self.flip,
            rotate=self.rotate,
            box=self.box,
        )

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkIcon(icon_name="mdi:file")
        page += mk.MkReprRawRendered(node, header="### With caption")

        node = MkIcon(icon_name="mdi:file", color="red")
        page += mk.MkReprRawRendered(node, header="### Colored")

        node = MkIcon(icon_name="mdi:file", rotate=90)
        page += mk.MkReprRawRendered(node, header="### Rotated")

        node = MkIcon(icon_name="mdi:file", height=100, width=100)
        page += mk.MkReprRawRendered(node, header="### Sized")


if __name__ == "__main__":
    img = MkIcon("mdi:file", rotate="90")
    print(img)