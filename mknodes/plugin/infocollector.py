from __future__ import annotations

from abc import ABCMeta
from collections.abc import Mapping, MutableMapping
import logging

from typing import Any

import jinja2
import mergedeep

from mknodes.utils import helpers, jinjahelpers, log, reprhelpers, yamlhelpers


logger = logging.getLogger(__name__)


class InfoCollector(MutableMapping, metaclass=ABCMeta):
    """MkNodes InfoCollector."""

    def __init__(self, undefined: str = "silent", load_templates: bool = False):
        loader = jinjahelpers.resource_loader if load_templates else None
        behavior = jinjahelpers.UNDEFINED_BEHAVIOR[undefined]
        self.env = jinja2.Environment(undefined=behavior, loader=loader)
        self.variables: dict[str, Any] = {"log": log.log_stream.getvalue}
        filters = {"dump_yaml": yamlhelpers.dump_yaml, "styled": helpers.styled}
        self.env.filters.update(filters)
        self.set_mknodes_filters()
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
        try:
            template = self.env.from_string(markdown)
        except jinja2.exceptions.TemplateSyntaxError as e:
            logger.warning("Error when loading template: %s", e)
            return markdown
        variables = self.variables | (variables or {})
        try:
            return template.render(**variables)
        except jinja2.exceptions.UndefinedError as e:
            logger.warning("Error when rendering template: %s", e)
            return ""

    def render_template(self, template_name: str, variables=None):
        template = self.env.get_template(template_name)
        variables = self.variables | (variables or {})
        try:
            return template.render(**variables)
        except jinja2.exceptions.UndefinedError as e:
            logger.warning("Error when rendering template: %s", e)
            return ""

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
            "extra": dict(social=self.variables["social_info"]),
        }


if __name__ == "__main__":
    builder = InfoCollector()
    print(dict(builder))
