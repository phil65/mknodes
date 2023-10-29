from __future__ import annotations

import re

from typing import Literal, Self

from mknodes.data import datatypes
from mknodes.utils import yamlhelpers


HEADER = "---\n{options}---\n"

HEADER_RE = re.compile(r"\A-{3}\n([\S\s]*)^-{3}(\n|$)", re.MULTILINE)


SectionStr = Literal["navigation", "toc", "path", "tags", "footer", "feedback"]


class Metadata(dict):
    """The Metadata class is a subclassed Python dictionary.

    It is enhanced with properties for common metadata fields in order
    to get proper type hints. Since this object is a dict subclass, you can of
    course also add any non-documented stuff to the Metadata.
    """

    def __init__(self, *args, **kwargs):
        search_dict = {}
        if "search_boost" in kwargs and kwargs["search_boost"] is not None:
            search_dict["boost"] = kwargs.pop("search_boost")
        if "exclude_from_search" in kwargs and kwargs["exclude_from_search"] is not None:
            search_dict["exclude"] = kwargs.pop("exclude_from_search")
        if search_dict:
            kwargs["search"] = search_dict
        super().__init__(*args, **kwargs)
        if self.icon and "/" not in self.icon and ":" not in self.icon:
            self.icon = f"material/{self.icon}"
        if isinstance(self.hide, str):
            self.hide = [i.strip() for i in self.hide.split(",")]
        if self.hide is not None:
            self.hide = [i if i != "nav" else "navigation" for i in self.hide or []]

    @property
    def hide(self) -> list[SectionStr] | None:
        """A list of items which should be hidden from the page.

        MkDocs-Material supports `"navigation"`, `"toc"`, `"path"`, `"tags"`.
        """
        return self.get("hide")

    @hide.setter
    def hide(self, val: list[SectionStr] | str | None):
        self["hide"] = val

    @property
    def search_boost(self) -> float | None:
        """A multiplier to modify search relevance."""
        return self.get("search_boost")

    @search_boost.setter
    def search_boost(self, val: float | None):
        self["search_boost"] = val

    @property
    def exclude_from_search(self) -> bool | None:
        """Exclude this page from search."""
        return self.get("exclude_from_search")

    @exclude_from_search.setter
    def exclude_from_search(self, val: bool | None):
        self["exclude_from_search"] = val

    @property
    def revision_date(self) -> bool | None:
        """Date when page was last revised."""
        return self.get("git_revision_date_localized")

    @revision_date.setter
    def revision_date(self, val: bool | None):
        self["git_revision_date_localized"] = val

    @property
    def creation_date(self) -> bool | None:
        """Page creation date."""
        return self.get("git_creation_date_localized")

    @creation_date.setter
    def creation_date(self, val: bool | None):
        self["git_creation_date_localized"] = val

    @property
    def icon(self) -> str | None:
        """An icon for the page (Example: `"material/wrench"`)."""
        return self.get("icon")

    @icon.setter
    def icon(self, val: str | None):
        # if val and "/" not in val:
        #     val = f"material/{val}"
        self["icon"] = val

    @property
    def status(self) -> datatypes.PageStatusStr | str | None:
        """The status of the page.

        MkDocs-Material supports `"new"`, `"deprecated"` and `"encrypted"` by default
        by showing an icon in the site nav. Additional icons can be added during
        the build process via
        [MaterialTheme.add_status_icon][mknodes.MaterialTheme.add_status_icon].
        """
        return self.get("status")

    @status.setter
    def status(self, val: datatypes.PageStatusStr | str | None):
        self["status"] = val

    @property
    def title(self) -> str | None:
        """Title for the page."""
        return self.get("title")

    @title.setter
    def title(self, val: str | None):
        self["title"] = val

    @property
    def subtitle(self) -> str | None:
        """Subtitle for the page."""
        return self.get("subtitle")

    @subtitle.setter
    def subtitle(self, val: str | None):
        self["subtitle"] = val

    @property
    def description(self) -> str | None:
        """Description text for the page."""
        return self.get("description")

    @description.setter
    def description(self, val: str | None):
        self["description"] = val

    @property
    def inclusion_level(self) -> str | None:
        """Page inclusion level."""
        return self.get("inclusion_level")

    @inclusion_level.setter
    def inclusion_level(self, val: str | None):
        self["inclusion_level"] = val

    @property
    def template(self) -> str | None:
        """Filename of the template the page should use.

        This is only a reference, you still need to add the template to the theme.
        """
        return self.get("template")

    @template.setter
    def template(self, val: str | None):
        self["template"] = val

    @property
    def tags(self) -> list[str]:
        """A list of tags associated with the page."""
        return self.get("tags", [])

    @tags.setter
    def tags(self, val: list[str] | None):
        self["tags"] = val

    @property
    def search(self) -> dict | None:
        """A dictionary containing search-related settings (`"boost"` / `"exclude"`)."""
        return self.get("search")

    @search.setter
    def search(self, val: dict | None):
        self["search"] = val

    @property
    def render_macros(self) -> bool | None:
        """Whether this page should get rendered by the templating engine."""
        return self.get("render_macros")

    @render_macros.setter
    def render_macros(self, val: bool | None):
        self["render_macros"] = val

    @classmethod
    def parse(cls, text: str) -> tuple[Self, str]:
        """Parse given text for metadata and return a (Metadata, Rest-from-text) tuple."""
        dct = {}
        if match := HEADER_RE.match(text):
            content = match[1]
            dct = yamlhelpers.load_yaml(content)
            text = text[match.span()[1] :]
        return cls(**dct), text

    def __str__(self):
        dct = {k: v for k, v in self.items() if v is not None}
        return yamlhelpers.dump_yaml(dct) if dct else ""

    def as_page_header(self) -> str:
        """Format metadata in Page header format (with --- separators)."""
        text = str(self)
        return HEADER.format(options=text) if text else ""


if __name__ == "__main__":
    metadata = Metadata(hide="toc", search_boost=2)
    print(metadata)
