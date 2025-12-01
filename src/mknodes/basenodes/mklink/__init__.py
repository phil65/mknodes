from __future__ import annotations

import inspect
import os
import types
from typing import TYPE_CHECKING, Any
from collections.abc import Mapping
import json
from mknodes.basenodes import mknode
from mknodes.utils import icons, log
from upathtools import to_upath

if TYPE_CHECKING:
    from collections.abc import Sequence
    from mknodes.info import linkprovider

logger = log.get_logger(__name__)


class MkLink(mknode.MkNode):
    """A simple Link (with optional icon and option to show up as a button).

    If no title is given, the URL is used as a title.
    """

    ICON = "octicons/link-24"
    ATTR_LIST_SEPARATOR = ""

    def __init__(
        self,
        target: linkprovider.LinkableType,
        title: str | None = None,
        *,
        tooltip: str | None = None,
        icon: str | None = None,
        as_button: bool = False,
        primary_color: bool = False,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            target: Link target
            title: Title used for link
            tooltip: Tooltip for the link
            icon: Optional icon to be displayed in front of title
            as_button: Whether link should be rendered as button
            primary_color: If rendered as button, use primary color as background.
            kwargs: keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.target = target
        self._title = title
        self.tooltip = tooltip
        self.as_button = as_button
        self.primary_color = primary_color
        self._icon = icon
        if as_button:
            self.add_css_class("md-button")
        if primary_color:
            self.add_css_class("md-button--primary")

    @property
    def icon(self) -> str:
        return icons.get_emoji_slug(self._icon) if self._icon else ""

    async def get_url(self) -> str:
        return await self.ctx.links.get_url(self.target)

    async def get_title(self) -> str:
        return self._title or await self.get_url()

    @classmethod
    def for_pydantic_playground(
        cls,
        files: Mapping[str, str] | list[types.ModuleType] | Sequence[str | os.PathLike[str]],
        title: str = "Open in Pydantic Playground",
        active_index: int = 0,
        **kwargs: Any,
    ) -> MkLink:
        """Create a link to Pydantic playground with pre-populated files.

        Args:
            files: The files to include in the playground. Can be:
                    - A mapping of filenames to code content
                    - A list of modules
                    - A list of file paths
            title: The title of the link
            active_index: The index of the active file in the playground
            **kwargs: Additional keyword arguments to pass to the Pydantic playground

        Returns:
            An MkLink instance pointing to the Pydantic playground
        """
        from urllib.parse import quote

        match files:
            case Mapping():
                file_data: list[dict[str, Any]] = [
                    {"name": name, "content": content} for name, content in files.items()
                ]
            case [types.ModuleType(), *_]:
                file_data = [
                    {"name": f"{mod.__name__}.py", "content": inspect.getsource(mod)}  # type: ignore
                    for mod in files
                ]
            case [str() | os.PathLike(), *_]:
                file_data = []
                for path in files:
                    file = to_upath(path)
                    file_data.append({
                        "name": file.name,
                        "content": file.read_text("utf-8"),
                    })
            case _:
                raise TypeError(files)

        # Add activeIndex to first file
        if file_data:
            file_data[active_index]["activeIndex"] = 1

        json_str = json.dumps(file_data)
        encoded = quote(json_str)

        url = f"https://pydantic.run/new?files={encoded}"
        return cls(url, title, **kwargs)

    async def to_md_unprocessed(self) -> str:
        prefix = f"{self.icon} " if self.icon else ""
        tooltip = f" {self.tooltip!r}" if self.tooltip else ""
        return f"[{prefix}{await self.get_title()}]({await self.get_url()}{tooltip})"


if __name__ == "__main__":
    import pathlib

    link = MkLink.for_pydantic_playground([pathlib.Path(__file__)])
    print(link)
