from __future__ import annotations

from abc import ABCMeta
from collections.abc import Mapping, MutableMapping
from importlib import util
import logging

from typing import Any

import jinja2
import mergedeep

from mknodes import project as project_
from mknodes.pages import mkpage
from mknodes.utils import helpers, reprhelpers, yamlhelpers


logger = logging.getLogger(__name__)


class LaxUndefined(jinja2.Undefined):
    """Pass anything wrong as blank."""

    def _fail_with_undefined_error(self, *args, **kwargs):
        return ""


UNDEFINED_BEHAVIOR = {
    "keep": jinja2.DebugUndefined,
    "silent": jinja2.Undefined,
    "strict": jinja2.StrictUndefined,
    # lax will even pass unknown objects:
    "lax": LaxUndefined,
}


class InfoCollector(MutableMapping, metaclass=ABCMeta):
    """MkNodes InfoCollector."""

    def __init__(self, undefined: str = "silent", load_templates: bool = False):
        if load_templates:
            loader = jinja2.FileSystemLoader(searchpath="mknodes/resources")
        else:
            loader = None
        behavior = UNDEFINED_BEHAVIOR[undefined]
        self.env = jinja2.Environment(undefined=behavior, loader=loader)
        self.variables: dict[str, Any] = {}
        filters = {"dump_yaml": yamlhelpers.dump_yaml, "styled": helpers.styled}
        self.env.filters.update(filters)
        self.set_mknodes_filters()
        if util.find_spec("markdown_exec"):
            self.set_markdown_exec_namespace()

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
        import functools

        import mknodes

        filters = {}
        for kls_name in mknodes.__all__:
            kls = getattr(mknodes, kls_name)
            fn = functools.partial(kls, parent=parent) if parent else kls
            filters[kls_name] = fn
        self.env.filters.update(filters)

    def merge(self, other: Mapping, additive: bool = False):
        strategy = mergedeep.Strategy.ADDITIVE if additive else mergedeep.Strategy.REPLACE
        self.variables = dict(mergedeep.merge(self.variables, other, strategy=strategy))

    def set_markdown_exec_namespace(self):
        from markdown_exec.formatters import python

        python._sessions_globals["mknodes"] = self.variables

    def get_info_from_project(self, project: project_.Project):
        metadata = project.folderinfo.aggregate_info() | project.theme.aggregate_info()
        variables = {
            "metadata": metadata,
            "filenames": {},
            "project": project,
            "social_info": project.folderinfo.get_social_info(),
        }
        variables |= project.get_requirements()
        if root := project._root:
            page_mapping = {
                node.resolved_file_path: node
                for _level, node in root.iter_nodes()
                if isinstance(node, mkpage.MkPage)
            }
            variables["page_mapping"] = page_mapping
            variables["filenames"] = list(page_mapping.keys())
        self.variables |= variables

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
        project = self.variables["project"]
        return {
            "repo_url": self.variables["metadata"]["repository_url"],
            "site_description": self.variables["metadata"]["summary"],
            "site_name": self.variables["metadata"]["name"],
            "site_author": project.info.author_name,
            "markdown_extensions": list(project.all_markdown_extensions().keys()),
            "plugins": list(self.variables["plugins"]),
            "mdx_configs": project.all_markdown_extensions(),
            "extra": dict(social=self.variables["social_info"]),
        }


if __name__ == "__main__":
    builder = InfoCollector()
    builder.get_info_from_project(project_.Project.for_mknodes())
    print(dict(builder))
