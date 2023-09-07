from __future__ import annotations

from abc import ABCMeta
from collections.abc import Mapping, MutableMapping
import logging

from typing import Any

import mergedeep

from mknodes.jinja import environment
from mknodes.utils import jinjahelpers, reprhelpers


logger = logging.getLogger(__name__)


class InfoCollector(MutableMapping, metaclass=ABCMeta):
    """MkNodes InfoCollector."""

    def __init__(self, *, undefined: str = "silent", load_templates: bool = False):
        self.env = environment.Environment(
            undefined=undefined,
            load_templates=load_templates,
        )
        self.variables: dict[str, Any] = {}
        jinjahelpers.set_markdown_exec_namespace(self.variables)

    def __getitem__(self, index):
        return self.variables[index]

    def __setitem__(self, index, value):
        self.variables[index] = value

    def __delitem__(self, index):
        del self.variables[index]

    def __iter__(self):
        return iter(self.variables.keys())

    def __len__(self):
        return len(self.variables)

    def __repr__(self):
        return reprhelpers.get_repr(self, self.variables)

    def set_mknodes_filters(self, parent=None):
        filters = jinjahelpers.get_mknodes_macros(parent)
        self.env.filters.update(filters)

    def merge(self, other: Mapping, additive: bool = False):
        strategy = mergedeep.Strategy.ADDITIVE if additive else mergedeep.Strategy.REPLACE
        self.variables = dict(mergedeep.merge(self.variables, other, strategy=strategy))

    def render(self, markdown: str, variables=None):
        variables = self.variables | (variables or {})
        return self.env.render_string(markdown, variables)

    def render_template(self, template_name: str, variables=None):
        variables = self.variables | (variables or {})
        return self.env.render_template(template_name, variables)

    def create_config(self):
        return {
            "repo_url": self.variables["metadata"]["repository_url"],
            "site_description": self.variables["metadata"]["summary"],
            "site_name": self.variables["metadata"]["name"],
            "site_author": self.variables["project"].info.author_name,
            "markdown_extensions": list(self.variables["markdown_extensions"].keys()),
            "plugins": list(self.variables["plugins"]),
            # "templates": list(self.variables["templates"].keys()),
            "mdx_configs": self.variables["markdown_extensions"],
            "extra": dict(social=self.variables["metadata"]["social_info"]),
        }


if __name__ == "__main__":
    builder = InfoCollector()
    print(dict(builder))
