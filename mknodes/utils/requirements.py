from __future__ import annotations

import collections.abc
import dataclasses

from mknodes.pages import pagetemplate


@dataclasses.dataclass
class Requirements(collections.abc.Mapping):
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


if __name__ == "__main__":
    req = Requirements()
    print(dict(req))
