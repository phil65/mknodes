from __future__ import annotations

import logging
import os
import pathlib

from typing import Any, Self

from mknodes.basenodes import mkcontainer, mkfootnotes, mknode, processors
from mknodes.data import datatypes
from mknodes.pages import metadata, pagetemplate
from mknodes.utils import reprhelpers


logger = logging.getLogger(__name__)


class MkPage(mkcontainer.MkContainer):
    """A node container representing a Markdown page.

    A page contains a list of other Markdown nodes, has a virtual Markdown file
    associated, and can have metadata (added as header)
    """

    ICON = "fontawesome/solid/sheet-plastic"

    def __init__(
        self,
        title: str | None = None,
        *,
        hide_toc: bool | None = None,
        hide_nav: bool | None = None,
        hide_path: bool | None = None,
        hide_tags: bool | None = None,
        search_boost: float | None = None,
        exclude_from_search: bool | None = None,
        icon: str | None = None,
        path: str | os.PathLike | None = None,
        status: datatypes.PageStatusStr | None = None,
        subtitle: str | None = None,
        description: str | None = None,
        template: str | pagetemplate.PageTemplate | None = None,
        virtual: bool = False,
        tags: list[str] | None = None,
        edit_path: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            path: Page path
            hide_toc: Whether TOC should be shown when this page is displayed.
            hide_nav: Whether Nav should be shown when this page is displayed.
            hide_path: Whether Breadcrumbs should be shown when this page is displayed.
            hide_tags: Whether tags should be shown when this page is displayed.
            search_boost: Factor to modify search ranking
            exclude_from_search: Whether to exclude this page from search listings
            icon: Optional page icon
            status: Page status
            title: Page title
            subtitle: Page subtitle
            description: Page description
            template: Page template (filename relative to `overrides` directory or
                       PageTemplate object)
            virtual: Whether the Page should result in a file. Mainly for testing purposes
            tags: tags to show above the main headline and within the search preview
            edit_path: Custom edit path for this page
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self._path = str(path) if path else None
        # import inspect
        # self._edit_path = pathlib.Path(inspect.currentframe().f_back.f_code.co_filename)
        self._edit_path = edit_path
        self.footnotes = mkfootnotes.MkFootNotes(parent=self)
        self.virtual = virtual
        self.metadata = metadata.Metadata(
            hide_toc=hide_toc,
            hide_nav=hide_nav,
            hide_path=hide_path,
            hide_tags=hide_tags,
            search_boost=search_boost,
            exclude_from_search=exclude_from_search,
            icon=icon,
            status=status,
            subtitle=subtitle,
            title=title,
            description=description,
            template=None,
            tags=tags,
        )
        self.template = template
        logger.info("Created MkPage %s", self.resolved_file_path)

    def __repr__(self):
        meta_kwargs = self.metadata.repr_kwargs()
        return reprhelpers.get_repr(self, path=str(self.path), **meta_kwargs)

    def __str__(self):
        return self.to_markdown()

    @property
    def path(self):
        if self._path:
            return self._path if self._path.endswith(".md") else f"{self._path}.md"
        return f"{self.title}.md"

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def resolved_file_path(self) -> str:
        """Returns the resulting section/subsection/../filename.xyz path."""
        path = "/".join(self.resolved_parts) + "/" + self.path
        return path.lstrip("/")

    @property
    def status(self) -> datatypes.PageStatusStr | None:
        return self.metadata.status

    @status.setter
    def status(self, value: datatypes.PageStatusStr):
        self.metadata.status = value

    @property
    def title(self) -> str | None:
        return self.metadata.title

    @title.setter
    def title(self, value: str):
        self.metadata.title = value

    @property
    def subtitle(self) -> str | None:
        return self.metadata.subtitle

    @subtitle.setter
    def subtitle(self, value: str):
        self.metadata.subtitle = value

    @property
    def icon(self) -> str | None:
        return self.metadata.icon

    @icon.setter
    def icon(self, value: str):
        self.metadata.icon = value

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value: str | pagetemplate.PageTemplate | None):
        if isinstance(value, pagetemplate.PageTemplate):
            self.metadata.template = value.filename
            self._template = value
        else:
            self.metadata.template = value
            self._template = None

    @classmethod
    def from_file(
        cls,
        path: str | os.PathLike,
        hide_toc: bool | None = None,
        hide_nav: bool | None = None,
        hide_path: bool | None = None,
        parent: mknode.MkNode | None = None,
    ) -> Self:
        """Reads file content and creates an MkPage.

        Parses and reads header metadata.

        Arguments:
            path: Path to load file from
            hide_toc: Hide Toc. Overrides parsed metadata if set.
            hide_nav: Hide Navigation. Overrides parsed metadata if set.
            hide_path: Hide Path. Overrides parsed metadata if set.
            parent: Optional parent for new page
        """
        path = pathlib.Path(path)
        file_content = path.read_text()
        data, text = metadata.Metadata.parse(file_content)
        if hide_toc is not None:
            data.hide_toc = hide_toc
        if hide_nav is not None:
            data.hide_nav = hide_nav
        if hide_path is not None:
            data.hide_path = hide_path
        page = cls(path=str(path), content=text, parent=parent)
        page.metadata = data
        return page

    def virtual_files(self) -> dict[str, str | bytes]:
        dct = {} if self.virtual else {self.path: self.to_markdown()}
        return dct | super().virtual_files()

    def get_processors(self):
        import mknodes

        procs = [
            processors.PrependMetadataProcessor(self.metadata),
            processors.FootNotesProcessor(self),
            processors.AnnotationProcessor(self),
        ]
        if any(
            isinstance(node, mknodes.MkNav) and node.append_markdown_to_pages
            for node in self.ancestors
        ):
            proc = processors.GeneratedMarkdownProcessor(self)
            procs.append(proc)
        return procs

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
