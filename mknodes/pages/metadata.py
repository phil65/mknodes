from __future__ import annotations

import dataclasses
import re

from typing import Self

from mknodes.data import datatypes
from mknodes.utils import yamlhelpers


HEADER = "---\n{options}---\n"

HEADER_RE = re.compile(r"\A-{3}\n([\S\s]*)^-{3}(\n|$)", re.MULTILINE)


@dataclasses.dataclass
class Metadata:
    hide_toc: bool | None = None
    hide_nav: bool | None = None
    hide_path: bool | None = None
    hide_tags: bool | None = None
    search_boost: float | None = None
    exclude_from_search: bool | None = None
    icon: str | None = None
    status: datatypes.PageStatusStr | None = None
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    template: str | None = None
    tags: list[str] | None = None

    def __post_init__(self):
        if self.icon and "/" not in self.icon:
            self.icon = f"material/{self.icon}"

    @classmethod
    def parse(cls, text: str) -> tuple[Self, str]:
        dct = {}
        if match := HEADER_RE.match(text):
            content = match[1]
            dct = yamlhelpers.load_yaml(content)
            if hide := dct.pop("hide", None):
                dct["hide_toc"] = "toc" in hide
                dct["hide_nav"] = "navigation" in hide
                dct["hide_path"] = "path" in hide
                dct["hide_tags"] = "tags" in hide
            if search := dct.pop("search", None):
                dct["search_boost"] = search.get("boost")
                dct["exclude_from_search"] = search.get("exclude")
            text = text[match.span()[1] :]
        # TODO: right now, additional metadata would lead to an exception
        return cls(**dct), text

    def __getitem__(self, index: str):
        return dataclasses.asdict(self)[index]

    def __setitem__(self, index: str, value):
        self.__setattr__(index, value)

    def __str__(self):
        data = self.as_dict()
        return yamlhelpers.dump_yaml(data) if data else ""

    def __bool__(self):
        return bool(self.as_dict())

    def __iter__(self):
        return iter(self.as_dict().keys())

    def __len__(self):
        return len(self.as_dict())

    def as_page_header(self) -> str:
        text = str(self)
        return HEADER.format(options=text) if text else ""

    @property
    def hide(self):
        hide_list = []
        if self.hide_nav:
            hide_list.append("navigation")
        if self.hide_toc:
            hide_list.append("toc")
        if self.hide_path:
            hide_list.append("path")
        if self.hide_tags:
            hide_list.append("tags")
        return hide_list or None

    @property
    def search(self):
        search_dict = {}
        if self.search_boost is not None:
            search_dict["boost"] = self.search_boost
        if self.exclude_from_search is not None:
            search_dict["exclude"] = self.exclude_from_search
        return search_dict or None

    def as_dict(self) -> dict:
        data = dict(
            title=self.title,
            subtitle=self.subtitle,
            icon=self.icon,
            status=self.status,
            description=self.description,
            template=self.template,
            hide=self.hide,
            search=self.search,
            tags=self.tags,
        )
        return {k: v for k, v in data.items() if v is not None}

    def repr_kwargs(self) -> dict:
        data = dataclasses.asdict(self)
        return {k: v for k, v in data.items() if v is not None}


if __name__ == "__main__":
    metadata = Metadata(hide_toc=True, search_boost=2)
    print(metadata.as_dict())
    print(metadata.repr_kwargs())
