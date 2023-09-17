from __future__ import annotations

import dataclasses

from typing import Self

from mkdocs.utils import meta

from mknodes.data import datatypes
from mknodes.utils import yamlhelpers


HEADER = "---\n{options}---\n"


@dataclasses.dataclass
class Metadata:
    hide: list[str] | str | None = None
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
        if isinstance(self.hide, str):
            self.hide = [i.strip() for i in self.hide.split(",")]
        if self.hide is not None:
            self.hide = [i if i != "nav" else "navigation" for i in self.hide or []]

    @classmethod
    def parse(cls, text: str) -> tuple[Self, str]:
        text, metadata = meta.get_data(text)
        if (hide := metadata.pop("hide", None)) is not None:
            metadata["hide"] = hide
        if search := metadata.pop("search", None):
            metadata["search_boost"] = search.get("boost")
            metadata["exclude_from_search"] = search.get("exclude")
        return cls(**metadata), text

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
    metadata = Metadata(hide="toc", search_boost=2)
    print(metadata.as_dict())
    print(metadata.repr_kwargs())
