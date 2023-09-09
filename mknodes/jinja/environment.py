from __future__ import annotations

from collections.abc import Mapping
import datetime

import jinja2

from mknodes.utils import helpers, jinjahelpers, log, mergehelpers, yamlhelpers


logger = log.get_logger(__name__)


ENVIRONMENT_GLOBALS = {"log": log.log_stream.getvalue, "now": datetime.datetime.now}
ENVIRONMENT_FILTERS = {"dump_yaml": yamlhelpers.dump_yaml, "styled": helpers.styled}


class Environment(jinja2.Environment):
    """Jinja environment."""

    def __init__(self, *, undefined: str = "silent", load_templates: bool = False):
        loader = jinjahelpers.resource_loader if load_templates else None
        behavior = jinjahelpers.UNDEFINED_BEHAVIOR[undefined]
        super().__init__(undefined=behavior, loader=loader)
        self.filters.update(ENVIRONMENT_FILTERS)
        self.globals.update(ENVIRONMENT_GLOBALS)

    def set_mknodes_filters(self, parent=None):
        filters = jinjahelpers.get_mknodes_macros(parent)
        self.filters.update(filters)

    def merge_globals(self, other: Mapping, additive: bool = False):
        strategy = "additive" if additive else "replace"
        mapping = mergehelpers.merge_dicts(self.variables, other, strategy=strategy)
        self.variables = dict(mapping)

    def render_string(self, markdown: str, variables=None):
        try:
            template = self.from_string(markdown)
        except jinja2.exceptions.TemplateSyntaxError as e:
            logger.warning("Error when loading template: %s", e)
            return markdown
        variables = variables or {}
        try:
            return template.render(**variables)
        except jinja2.exceptions.UndefinedError as e:
            logger.warning("Error when rendering template: %s", e)
            return ""

    def render_template(self, template_name: str, variables=None):
        template = self.get_template(template_name)
        variables = variables or {}
        try:
            return template.render(**variables)
        except jinja2.exceptions.UndefinedError as e:
            logger.warning("Error when rendering template: %s", e)
            return ""


if __name__ == "__main__":
    from mknodes.project import Project

    env = Environment()
    proj = Project.for_mknodes()
    ctx = proj.context.as_dict()
    env.globals.update(ctx)
    text = env.render_string(r"{{ metadata.description }}")
    print(text)
