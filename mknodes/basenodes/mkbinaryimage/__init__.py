from __future__ import annotations

import upath

from typing import Any, Literal, Self, TYPE_CHECKING

from jinjarope import textfilters

from mknodes.basenodes import mkimage
from mknodes.utils import icons, log

if TYPE_CHECKING:
    from mknodes.info import linkprovider
    import os


logger = log.get_logger(__name__)


class MkBinaryImage(mkimage.MkImage):
    """Image carrying the data by itself.

    This node basically is a regular image link, but carries the image data by itself.
    The data will get written to the "virtual" folder at the end of the process.
    It can hold either str or bytes as data.
    """

    ICON = "material/file-image"

    def __init__(
        self,
        data: bytes | str,
        path: str,
        *,
        target: linkprovider.LinkableType | None = None,
        caption: str = "",
        title: str = "",
        align: Literal["left", "right"] | None = None,
        width: int | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            data: Image data
            path: path for the image (including extension)
            target: Optional URL or node the image should link to
            caption: Image caption
            title: Image title
            align: Image alignment
            width: Image width in pixels
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(
            path=path,
            target=target,
            caption=caption,
            title=title,
            align=align,
            width=width,
            **kwargs,
        )
        self.data = data

    @property
    def files(self) -> dict[str, str | bytes]:
        path = "/".join(self.resolved_parts) + "/" + self.path
        return {path: self.data} | self._files

    @classmethod
    def for_icon(cls, icon: str, **kwargs: Any) -> Self:
        """Return a MkBinaryImage with data for given icon.

        Arguments:
            icon: Icon to get a MkBinaryImage for (example: material/file-image)
            kwargs: Keyword arguments passed to constructor
        """
        content = icons.get_icon_svg(icon)
        path = f"{textfilters.slugify(icon)}.svg"
        return cls(data=content, path=path, **kwargs)

    @classmethod
    def for_file(
        cls,
        path: str | os.PathLike[str],
        storage_options: dict | None = None,
        **kwargs: Any,
    ) -> Self:
        """Return a MkBinaryImage with data for given icon.

        Arguments:
            path: Path to an image (also takes fsspec protocol URLs)
            storage_options: Options for fsspec backend
            kwargs: Keyword arguments passed to constructor
        """
        opts = storage_options or {}
        file = upath.UPath(path, **opts)
        return cls(data=file.read_bytes(), path=file.name, **kwargs)


if __name__ == "__main__":
    node = MkBinaryImage.for_file("assets/cli.gif")
    print(node.data)
