from __future__ import annotations

from collections.abc import Mapping
import contextlib
import datetime
import functools
import os
import pathlib

from typing import Any

import jinja2

from mknodes import paths
from mknodes.utils import (
    helpers,
    inspecthelpers,
    jinjahelpers,
    log,
    mergehelpers,
    yamlhelpers,
)


logger = log.get_logger(__name__)


@functools.cache
def load_file(path: str | os.PathLike) -> str:
    return pathlib.Path(path).read_text(encoding="utf-8")


ENVIRONMENT_GLOBALS = {
    "log": log.log_stream.getvalue,
    "now": datetime.datetime.now,
    "str": str,
    "inspecthelpers": inspecthelpers,
    "resources_dir": paths.RESOURCES,
}
ENVIRONMENT_FILTERS = {
    "dump_yaml": yamlhelpers.dump_yaml,
    "styled": helpers.styled,
    "rstrip": str.rstrip,
    "lstrip": str.lstrip,
    "removesuffix": str.removesuffix,
    "removeprefix": str.removeprefix,
    "issubclass": issubclass,
    "isinstance": isinstance,
    "hasattr": hasattr,
    "load_file": load_file,
    "path_join": os.path.join,
}


class Environment(jinja2.Environment):
    """Jinja environment."""

    def __init__(self, *, undefined: str = "silent", load_templates: bool = False):
        loader = jinjahelpers.resource_loader if load_templates else None
        behavior = jinjahelpers.UNDEFINED_BEHAVIOR[undefined]
        self.extra_files: set[str] = set()
        super().__init__(undefined=behavior, loader=loader)
        self.filters.update(ENVIRONMENT_FILTERS)
        self.globals.update(ENVIRONMENT_GLOBALS)

    def set_mknodes_filters(self, parent=None):
        """Set our MkNode filters.

        The filters are a partial with the parent already set, if parent is given.

        Arguments:
            parent: Node parent
        """
        filters = jinjahelpers.get_mknodes_macros(parent)
        self.filters.update(filters)
        # self.globals.update(filters)

    def merge_globals(self, other: Mapping, additive: bool = False):
        """Merge other into the environment globals with given strategy.

        Arguments:
            other: Globals to merge into environment
            additive: Whether an additive strategy should be used instead of replace.
        """
        strategy = "additive" if additive else "replace"
        mapping = mergehelpers.merge_dicts(self.variables, other, strategy=strategy)
        self.variables = dict(mapping)

    def render_string(self, markdown: str, variables: dict | None = None):
        """Render a template string.

        Arguments:
            markdown: String to render
            variables: Extra variables for the environment
        """
        try:
            template = self.from_string(markdown)
        except jinja2.exceptions.TemplateSyntaxError:
            logger.exception("Error when loading template.")
            return markdown
        variables = variables or {}
        try:
            return template.render(**variables)
        except jinja2.exceptions.UndefinedError:
            logger.exception("Error when rendering template.")
            return ""

    def add_template(self, file: str | os.PathLike):
        """Add a new template during runtime.

        Will create a new DictLoader and inject it into the existing loaders.

        Useful since render_string/render_file does not allow to use a parent template.
        Using this, render_template can be used.

        Arguments:
            file: File to add as a template
        """
        # we keep track of already added extra files to not add things multiple times.
        file = str(file)
        if file in self.extra_files:
            return
        self.extra_files.add(file)
        content = load_file(file)
        new_loader = jinja2.DictLoader({file: content})
        match self.loader:
            case jinja2.ChoiceLoader():
                self.loader.loaders = [new_loader, *self.loader.loaders]
            case None:
                self.loader = new_loader
            case _:
                self.loader = jinja2.ChoiceLoader(loaders=[new_loader, self.loader])

    def render_file(self, file: str | os.PathLike, variables: dict | None = None) -> str:
        """Helper to directly render a template from filesystem.

        Note: The file we pull in gets cached. That should be fine for our case though.

        Arguments:
            file: Template file to load
            variables: Extra variables for the environment
        """
        content = load_file(str(file))
        return self.render_string(content, variables)

    def render_template(
        self,
        template_name: str,
        variables: dict[str, Any] | None = None,
        parent_template: str | None = None,
    ):
        """Render a loaded template.

        Arguments:
            template_name: Template name
            variables: Extra variables for this render call
            parent_template: Optional parent template (to be used with super())
        """
        template = self.get_template(template_name, parent=parent_template)
        variables = variables or {}
        return template.render(**variables)

    @contextlib.contextmanager
    def with_globals(self, **kwargs):
        """Context manager to temporarily set globals for the environment.

        Arguments:
            kwargs: Globals to set
        """
        self.globals.update(kwargs)
        yield
        for k in kwargs:
            del self.globals[k]


if __name__ == "__main__":
    # from mknodes.project import Project

    env = Environment()
    env.set_mknodes_filters()
    print(env.loader)
    env.add_template("mknodes/resources/requirements.md")
    env.get_template("mknodes/resources/requirements.md")
    # proj = Project.for_mknodes()
    # ctx = proj.context.as_dict()
    # env.globals.update(ctx)
    # text = env.render_string("{{ 'TTset' | isinstance(str) }}")
    # print(text)
