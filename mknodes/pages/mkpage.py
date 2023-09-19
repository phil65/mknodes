from __future__ import annotations

from collections.abc import Callable
import inspect
import os
import pathlib

from typing import Any, Self
from urllib import parse

from mknodes.basenodes import mkcontainer, mkfootnotes, mknode, processors
from mknodes.data import datatypes
from mknodes.navs import mknav
from mknodes.pages import metadata, pagetemplate
from mknodes.utils import downloadhelpers, helpers, log, reprhelpers, requirements


logger = log.get_logger(__name__)


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
        hide: list[str] | str | None = None,
        search_boost: float | None = None,
        exclude_from_search: bool | None = None,
        icon: str | None = None,
        path: str | os.PathLike | None = None,
        status: datatypes.PageStatusStr | None = None,
        subtitle: str | None = None,
        description: str | None = None,
        template: str | pagetemplate.PageTemplate | None = None,
        inclusion_level: bool | None = True,
        tags: list[str] | None = None,
        edit_path: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            path: Page path
            hide: Hide parts of the website ("toc", "nav", "path", "tags").
            search_boost: Factor to modify search ranking
            exclude_from_search: Whether to exclude this page from search listings
            icon: Optional page icon
            status: Page status
            title: Page title
            subtitle: Page subtitle
            description: Page description
            template: Page template (filename relative to `overrides` directory or
                       PageTemplate object)
            inclusion_level: Inclusion level of the page
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
        self.inclusion_level = inclusion_level
        self.created_by: Callable | None = None
        self._metadata = metadata.Metadata(
            hide=hide,
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
        frame = i.f_back.f_back if (i := inspect.currentframe()) else None  # type: ignore[union-attr]  # noqa: E501
        if frame:
            fn_name = qual if (qual := frame.f_code.co_qualname) != "<module>" else None
            self._metadata["created"] = dict(
                source_filename=frame.f_code.co_filename,
                source_function=fn_name,
                source_line_no=frame.f_lineno,
                # klass=frame.f_locals["self"].__class__.__name__,
            )
        logger.debug("Created %s, %r", type(self).__name__, self.resolved_file_path)

    def __repr__(self):
        return reprhelpers.get_repr(self, path=str(self.path), **self._metadata)

    def get_node_requirements(self):
        templates = [self.template] if self.template else []
        return requirements.Requirements(templates=templates)

    def is_index(self) -> bool:
        """Returns True if the page is the index page for the parent Nav."""
        return self.parent.index_page is self if self.parent else False

    @property
    def metadata(self) -> metadata.Metadata:
        """Return page metadata, complemented with the parent Nav metadata objects."""
        meta = metadata.Metadata()
        navs = [i for i in self.ancestors if isinstance(i, mknav.MkNav)]
        for nav in reversed(navs):
            meta.update(nav.metadata)
        meta.update(self._metadata)
        return meta

    @metadata.setter
    def metadata(self, val: metadata.Metadata):
        self._metadata = val

    @property
    def path(self):
        if self._path:
            return self._path.removesuffix(".md") + ".md"
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
        self._metadata.status = value

    @property
    def title(self) -> str | None:
        return self.metadata.title

    @title.setter
    def title(self, value: str):
        self._metadata.title = value

    @property
    def subtitle(self) -> str | None:
        return self.metadata.subtitle

    @subtitle.setter
    def subtitle(self, value: str):
        self._metadata.subtitle = value

    @property
    def icon(self) -> str | None:
        return self.metadata.icon

    @icon.setter
    def icon(self, value: str):
        self._metadata.icon = value

    @property
    def template(self) -> pagetemplate.PageTemplate | None:
        return self._template

    @template.setter
    def template(self, value: str | pagetemplate.PageTemplate | None):
        if isinstance(value, pagetemplate.PageTemplate):
            self._metadata.template = value.filename
            self._template = value
        else:
            self._metadata.template = value
            self._template = None

    @classmethod
    def from_file(
        cls,
        path: str | os.PathLike,
        title: str | None = None,
        hide: str | list[str] | None = None,
        parent: mknode.MkNode | None = None,
    ) -> Self:
        """Reads file content and creates an MkPage.

        Parses and reads header metadata.

        Arguments:
            path: Path to load file from
            title: Optional title to use
                   If None, title will be infered from metadata or filename
            hide: Hide parts of the page ("toc", "nav", "tags", "path")
            parent: Optional parent for new page
        """
        if helpers.is_url(url := str(path)):
            file_content = downloadhelpers.download(url).decode()
            split = parse.urlsplit(url)
            path = f"{title}.md" if title else pathlib.Path(split.path).name
            path = pathlib.Path(path)
        else:
            path = pathlib.Path(path)
            file_content = path.read_text()
        data, text = metadata.Metadata.parse(file_content)
        if hide is not None:
            data.hide = hide
        page = cls(path=path.name, content=text, title=title, parent=parent)
        page.metadata = data
        return page

    def get_processors(self):
        """Override base MkNode processors."""
        return [
            processors.PrependMetadataProcessor(self.metadata),
            processors.FootNotesProcessor(self),
            processors.AnnotationProcessor(self),
        ]


if __name__ == "__main__":
    doc = MkPage.from_file(
        "https://raw.githubusercontent.com/mkdocs/mkdocs/master/docs/getting-started.md",
    )
    print(doc)
    # print(doc.children)
