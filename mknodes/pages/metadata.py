from __future__ import annotations

from typing import Self

from mkdocs.utils import meta

from mknodes.data import datatypes
from mknodes.utils import yamlhelpers


HEADER = "---\n{options}---\n"


class Metadata(dict):
    """Metadata is a dict with some common keys exposed as properties."""

    def __init__(self, *args, **kwargs):
        search_dict = {}
        if "search_boost" in kwargs and kwargs["search_boost"] is not None:
            search_dict["boost"] = kwargs.pop("search_boost")
        if "exclude_from_search" in kwargs and kwargs["exclude_from_search"] is not None:
            search_dict["exclude"] = kwargs.pop("exclude_from_search")
        if search_dict:
            kwargs["search"] = search_dict
        super().__init__(*args, **kwargs)
        if self.icon and "/" not in self.icon:
            self.icon = f"material/{self.icon}"
        if isinstance(self.hide, str):
            self.hide = [i.strip() for i in self.hide.split(",")]
        if self.hide is not None:
            self.hide = [i if i != "nav" else "navigation" for i in self.hide or []]

    @property
    def hide(self) -> list[str] | str | None:
        return self.get("hide")

    @hide.setter
    def hide(self, val: list[str] | str | None):
        self["hide"] = val

    @property
    def search_boost(self) -> float | None:
        return self.get("search_boost")

    @search_boost.setter
    def search_boost(self, val: float | None):
        self["search_boost"] = val

    @property
    def exclude_from_search(self) -> bool | None:
        return self.get("exclude_from_search")

    @exclude_from_search.setter
    def exclude_from_search(self, val: bool | None):
        self["exclude_from_search"] = val

    @property
    def icon(self) -> str | None:
        return self.get("icon")

    @icon.setter
    def icon(self, val: str | None):
        # if val and "/" not in val:
        #     val = f"material/{val}"
        self["icon"] = val

    @property
    def status(self) -> datatypes.PageStatusStr | None:
        return self.get("status")

    @status.setter
    def status(self, val: datatypes.PageStatusStr | None):
        self["status"] = val

    @property
    def title(self) -> str | None:
        return self.get("title")

    @title.setter
    def title(self, val: str | None):
        self["title"] = val

    @property
    def subtitle(self) -> str | None:
        return self.get("subtitle")

    @subtitle.setter
    def subtitle(self, val: str | None):
        self["subtitle"] = val

    @property
    def description(self) -> str | None:
        return self.get("description")

    @description.setter
    def description(self, val: str | None):
        self["description"] = val

    @property
    def template(self) -> str | None:
        return self.get("template")

    @template.setter
    def template(self, val: str | None):
        self["template"] = val

    @property
    def tags(self) -> list[str] | None:
        return self.get("tags")

    @tags.setter
    def tags(self, val: list[str] | None):
        self["tags"] = val

    @property
    def search(self) -> dict | None:
        return self.get("search")

    @search.setter
    def search(self, val: dict | None):
        self["search"] = val

    @classmethod
    def parse(cls, text: str) -> tuple[Self, str]:
        text, metadata = meta.get_data(text)
        if (hide := metadata.pop("hide", None)) is not None:
            metadata["hide"] = hide
        if search := metadata.pop("search", None):
            metadata["search_boost"] = search.get("boost")
            metadata["exclude_from_search"] = search.get("exclude")
        return cls(**metadata), text

    def __str__(self):
        dct = {k: v for k, v in self.items() if v is not None}
        return yamlhelpers.dump_yaml(dct) if dct else ""

    def as_page_header(self) -> str:
        text = str(self)
        return HEADER.format(options=text) if text else ""


if __name__ == "__main__":
    metadata = Metadata(hide="toc", search_boost=2)
    print(metadata)
