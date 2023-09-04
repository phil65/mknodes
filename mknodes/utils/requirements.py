from __future__ import annotations

import abc
import collections.abc
import dataclasses

import mergedeep

from mknodes.pages import pagetemplate


@dataclasses.dataclass
class Requirements(collections.abc.Mapping, metaclass=abc.ABCMeta):
    css: dict[str, str] = dataclasses.field(default_factory=dict)
    templates: list[pagetemplate.PageTemplate] = dataclasses.field(default_factory=list)
    markdown_extensions: dict[str, dict] = dataclasses.field(default_factory=dict)
    plugins: set[str] = dataclasses.field(default_factory=set)
    js_files: set[str] = dataclasses.field(default_factory=set)

    def __getitem__(self, value):
        return getattr(self, value)

    def __setitem__(self, index, value):
        setattr(self, index, value)

    def __len__(self):
        return len(dataclasses.fields(self))

    def __iter__(self):
        return iter(i.name for i in dataclasses.fields(self))

    def merge(self, other: collections.abc.Mapping, additive: bool = False):
        strategy = mergedeep.Strategy.ADDITIVE if additive else mergedeep.Strategy.REPLACE
        result = dict(mergedeep.merge(self, other, strategy=strategy))
        for k, v in result.items():
            self[k] = v


if __name__ == "__main__":
    req = Requirements(css={"a.css": "CSS"})
    req.merge(dict(css={"b.css": "CSS"}))
    print(req)
