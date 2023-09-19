from __future__ import annotations

import abc
import collections.abc
import dataclasses

from mknodes.pages import pagetemplate
from mknodes.utils import mergehelpers


class Extension(dict):
    def __init__(self, extension_name: str, **kwargs):
        super().__init__(**kwargs)
        self.extension_name = extension_name

    def __str__(self):
        return self.extension_name

    def __hash__(self):
        return hash(self.extension_name + str(dict(self)))

    def as_mkdocs_dict(self):
        return {self.extension_name: dict(self)}


@dataclasses.dataclass
class Requirements(collections.abc.Mapping, metaclass=abc.ABCMeta):
    css: dict[str, str] = dataclasses.field(default_factory=dict)
    """A filepath->filecontent dictionary containing the required CSS."""
    templates: list[pagetemplate.PageTemplate] = dataclasses.field(default_factory=list)
    """A list of required templates."""
    markdown_extensions: dict[str, dict] = dataclasses.field(default_factory=dict)
    """A extension_name->settings dictionary containing the required md extensions."""
    plugins: set[str] = dataclasses.field(default_factory=set)
    """A set of required plugins. (Only for info purposes)"""
    js_files: dict[str, str] = dataclasses.field(default_factory=dict)
    """A filepath->filecontent dictionary containing the required JS files."""

    def __getitem__(self, value):
        return getattr(self, value)

    def __setitem__(self, index, value):
        setattr(self, index, value)

    def __len__(self):
        return len(dataclasses.fields(self))

    def __iter__(self):
        return iter(i.name for i in dataclasses.fields(self))

    def merge(self, other: collections.abc.Mapping, additive: bool = False):
        """Merge requirements with another requirements instance or dict.

        Adds requirements from other to this instance.

        Arguments:
            other: The requirements to merge into this one.
            additive: Merge strategy. Either additive or replace.
        """
        self.css |= other["css"]
        self.templates += other["templates"]
        if other_exts := other["markdown_extensions"]:
            exts = [self.markdown_extensions, other_exts]
            merged = mergehelpers.merge_extensions(exts)
            self.markdown_extensions = mergehelpers.merge_dicts(*merged)
        self.plugins |= other["plugins"]
        self.js_files |= other["js_files"]
        return self


if __name__ == "__main__":
    req = Requirements(css={"a.css": "CSS"})
    req.merge(dict(css={"b.css": "CSS"}))
    print(req)
