from __future__ import annotations

from abc import ABCMeta
from collections.abc import MutableMapping
from importlib import util
import logging

from typing import Any

import jinja2
import mergedeep

from mknodes import paths, project as project_
from mknodes.pages import mkpage
from mknodes.utils import reprhelpers


logger = logging.getLogger(__name__)


class InfoCollector(MutableMapping, metaclass=ABCMeta):
    """MkNodes InfoCollector."""

    def __init__(self, data: dict[str, Any] | None = None):
        self.env = jinja2.Environment()
        self.variables = data or {}
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

    def merge(self, other, additive: bool = False):
        strategy = mergedeep.Strategy.ADDITIVE if additive else mergedeep.Strategy.REPLACE
        self.variables = dict(mergedeep.merge(self.variables, other, strategy=strategy))

    def set_markdown_exec_namespace(self):
        from markdown_exec.formatters import python

        python._sessions_globals["mknodes"] = self.variables

    def get_info_from_project(self, project: project_.Project):
        self.variables["metadata"] = project.aggregate_info()
        self.variables["project"] = project
        if root := project._root:
            js_files = {
                path: (paths.RESOURCES / path).read_text() for path in root.all_js_files()
            }
            infos = dict(
                files=project.all_files(),
                css=root.all_css(),
                js_files=js_files,
                theme_css=project.theme.css,
                markdown_extensions=project.all_markdown_extensions(),
                social_info=project.folderinfo.get_social_info(),
                templates=list(project.templates) + root.all_templates(),
            )
            self.variables.update(infos)
            page_mapping = {
                node.resolved_file_path: node
                for _level, node in root.iter_nodes()
                if isinstance(node, mkpage.MkPage)
            }
            self.variables["page_mapping"] = page_mapping

    def render(self, markdown: str):
        md_template = self.env.from_string(markdown)
        return md_template.render(**self.variables)


if __name__ == "__main__":
    builder = InfoCollector()
    builder.get_info_from_project(project_.Project.for_mknodes())
    print(builder)
