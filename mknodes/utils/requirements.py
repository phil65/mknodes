from __future__ import annotations

import abc
import collections.abc
import dataclasses

from mknodes.pages import pagetemplate
from mknodes.utils import mergehelpers


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
        self.css |= other["css"]
        self.templates += other["templates"]
        mergehelpers.merge_dicts(self.markdown_extensions, other["markdown_extensions"])
        self.plugins |= other["plugins"]
        self.js_files |= other["js_files"]
        return self


if __name__ == "__main__":
    req = Requirements(css={"a.css": "CSS"})
    req.merge(dict(css={"b.css": "CSS"}))
    print(req)
