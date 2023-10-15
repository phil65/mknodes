from __future__ import annotations

import datetime
import functools

from importlib import util
import os
import pathlib
from typing import Any

import jinja2

from mknodes import paths
from mknodes.utils import helpers, inspecthelpers, log, reprhelpers, yamlhelpers


class PackageLoader(jinja2.PackageLoader):
    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            package_name=self.package_name,
            package_path=self.package_path,
        )


class FileSystemLoader(jinja2.FileSystemLoader):
    def __repr__(self):
        return reprhelpers.get_repr(self, searchpath=self.searchpath)


class ChoiceLoader(jinja2.ChoiceLoader):
    def __repr__(self):
        return reprhelpers.get_repr(self, loaders=self.loaders)


class DictLoader(jinja2.DictLoader):
    def __repr__(self):
        return reprhelpers.get_repr(self, mapping=self.mapping)


resources_loader = PackageLoader("mknodes", "resources")
docs_loader = FileSystemLoader(searchpath="docs/")
resource_loader = ChoiceLoader([resources_loader, docs_loader])


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
    "str": str,
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

# material_partials_loader = PackageLoader("material", "partials")


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


def set_markdown_exec_namespace(variables: dict[str, Any], namespace: str = "mknodes"):
    if util.find_spec("markdown_exec"):
        from markdown_exec.formatters import python

        python._sessions_globals[namespace] = variables
