from __future__ import annotations

import dataclasses
import re

from typing import Literal, Self

import yaml


HEADER = "---\n{options}---\n"

HEADER_RE = re.compile(r"\A-{3}\n([\S\s]*)^-{3}(\n|$)", re.MULTILINE)


@dataclasses.dataclass
class Metadata:
    hide_toc: bool | None = None
    hide_nav: bool | None = None
    hide_path: bool | None = None
    search_boost: float | None = None
    exclude_from_search: bool | None = None
    icon: str | None = None
    status: Literal["new", "deprecated"] | None = None
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    template: str | None = None

    @classmethod
    def parse(cls, text: str) -> tuple[Self, str]:
        dct = {}
        if match := HEADER_RE.match(text):
            content = match[1]
            dct = yaml.safe_load(content)
            if hide := dct.pop("hide", None):
                dct["hide_toc"] = "toc" in hide
                dct["hide_nav"] = "navigation" in hide
                dct["hide_path"] = "path" in hide
            if search := dct.pop("search", None):
                dct["search_boost"] = search.get("boost")
                dct["exclude_from_search"] = search.get("exclude")
            text = text[match.endpos :]
        # TODO: right now, additional metadata would lead to an exception
        return cls(**dct), text

    def __getitem__(self, index: str):
        return dataclasses.asdict(self)[index]

    def __setitem__(self, index: str, value):
        self.__setattr__(index, value)

    def __str__(self):
        data = self.as_dict()
        return yaml.dump(data, Dumper=yaml.Dumper, indent=2) if data else ""

    def __bool__(self):
        return bool(self.as_dict())

    def as_page_header(self) -> str:
        text = str(self)
        if not text:
            return ""
        return HEADER.format(options=text)

    @property
    def hide(self):
        hide_list = []
        if self.hide_nav:
            hide_list.append("navigation")
        if self.hide_toc:
            hide_list.append("toc")
        if self.hide_path:
            hide_list.append("path")
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
        )
        return {k: v for k, v in data.items() if v is not None}

    def repr_kwargs(self) -> dict:
        data = dataclasses.asdict(self)
        return {k: v for k, v in data.items() if v is not None}


if __name__ == "__main__":
    metadata = Metadata(hide_toc=True, search_boost=2)
    print(metadata.as_dict())
    print(metadata.repr_kwargs())
