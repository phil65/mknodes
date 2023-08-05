from __future__ import annotations

import logging
import os
import pathlib

from typing import Any, Literal

from typing_extensions import Self
import yaml

from mknodes.basenodes import mkadmonition, mkcontainer, mkfootnotes, mkhtmlblock
from mknodes.utils import helpers


logger = logging.getLogger(__name__)

HEADER = "---\n{options}---\n\n"


class MkPage(mkcontainer.MkContainer):
    """A node container representing a Markdown page.

    A page contains a list of other Markdown nodes, has a virtual Markdown file
    associated, and can have metadata (added as header)
    """

    ICON = "fontawesome/solid/sheet-plastic"

    def __init__(
        self,
        path: str | os.PathLike = "",
        *,
        hide_toc: bool | None = None,
        hide_nav: bool | None = None,
        hide_path: bool | None = None,
        search_boost: float | None = None,
        exclude_from_search: bool | None = None,
        icon: str | None = None,
        status: Literal["new", "deprecated"] | None = None,
        title: str | None = None,
        subtitle: str | None = None,
        description: str | None = None,
        template: str | None = None,
        append_markdown: bool | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            path: Page path
            hide_toc: Whether TOC should be shown when this page is displayed.
            hide_nav: Whether Nav should be shown when this page is displayed.
            hide_path: Whether Breadcrumbs should be shown when this page is displayed.
            search_boost: Factor to modify search ranking
            exclude_from_search: Whether to exclude this page from search listings
            icon: Optional page icon
            status: Page status
            title: Page title
            subtitle: Page subtitle
            description: Page description
            template: Page template (filename relative to `overrides` directory)
            append_markdown: Whether pages should contain a collapsible admonition
                             containing the markup at the bottom. Setting is
                             inherited from the parent navs if not set.
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.path = str(path)
        if not self.path.endswith(".md"):
            self.path += ".md"
        self.footnotes = mkfootnotes.MkFootNotes(parent=self)
        self.append_markdown = append_markdown
        self.metadata: dict[str, Any] = {}
        if hide_toc is not None:
            self.metadata.setdefault("hide", []).append("toc")
        if hide_nav is not None:
            self.metadata.setdefault("hide", []).append("navigation")
        if hide_path is not None:
            self.metadata.setdefault("hide", []).append("path")
        if search_boost is not None:
            self.metadata.setdefault("search", {})["boost"] = search_boost
        if exclude_from_search is not None:
            self.metadata.setdefault("search", {})["exclude"] = exclude_from_search
        if icon is not None:
            self.metadata["icon"] = icon
        if status is not None:
            self.metadata["status"] = status
        if subtitle is not None:
            self.metadata["subtitle"] = subtitle
        if title is not None:
            self.metadata["title"] = title
        if description is not None:
            self.metadata["description"] = description
        if template is not None:
            self.metadata["template"] = template

    def __repr__(self):
        meta_kwargs = {k: v for k, v in self.metadata.items() if v is not None}
        return helpers.get_repr(self, path=str(self.path), **meta_kwargs)

    def __str__(self):
        return self.to_markdown()

    @property
    def status(self):
        return self.metadata.get("status")

    @status.setter
    def status(self, value: Literal["new", "deprecated"]):
        self.metadata["status"] = value

    @classmethod
    def from_file(
        cls,
        path: str | os.PathLike,
        hide_toc: bool | None = None,
        hide_nav: bool | None = None,
        hide_path: bool | None = None,
    ) -> Self:
        path = pathlib.Path(path)
        return cls(
            path.name,
            content=path.read_text(),
            hide_toc=hide_toc,
            hide_nav=hide_nav,
            hide_path=hide_path,
        )

    def virtual_files(self) -> dict[str, str]:
        return {self.path: self.to_markdown()}

    def to_markdown(self) -> str:
        from mknodes import mknav

        header = self.formatted_header()
        content_str = self._to_markdown()
        if self.footnotes:
            content_str = f"{content_str}\n\n{self.footnotes}"
        content_str = self.attach_annotations(content_str)
        text = header + content_str if header else content_str
        if self.append_markdown is False:
            return text
        for node in self.ancestors:
            if isinstance(node, mknav.MkNav) and node.append_markdown_to_pages:
                code = mkhtmlblock.MkHtmlBlock(text)
                admonition = mkadmonition.MkAdmonition(
                    code,
                    collapsible=True,
                    title="Markdown",
                )
                text += "\n"
                text += str(admonition)
                break
        return text

    def formatted_header(self) -> str:
        """Return the formatted header (containing metadata) for the page."""
        if not self.metadata:
            return ""
        options = yaml.dump(self.metadata, Dumper=yaml.Dumper, indent=2)
        return HEADER.format(options=options)

    def add_newlines(self, num: int):
        """Add line separators to the page.

        Arguments:
            num: Amount of newlines to add.
        """
        self.append("<br>" * num)


if __name__ == "__main__":
    doc = MkPage(hide_toc=True, search_boost=2)
    print(doc)
    # print(doc.children)
