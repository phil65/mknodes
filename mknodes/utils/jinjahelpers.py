from __future__ import annotations

from collections.abc import Callable
import datetime
import functools

from importlib import util
import os
import pathlib
from typing import Any

import jinja2

from mknodes import paths
from mknodes.utils import (
    helpers,
    inspecthelpers,
    log,
    yamlhelpers,
)


resources_loader = jinja2.FileSystemLoader(searchpath="mknodes/resources")
docs_loader = jinja2.FileSystemLoader(searchpath="docs/")
resource_loader = jinja2.ChoiceLoader([resources_loader, docs_loader])


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

# material_partials_loader = jinja2.PackageLoader("material", "partials")


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


def get_mknodes_macros(parent=None) -> dict[str, Callable]:
    import mknodes

    return {
        kls_name: (
            functools.partial(getattr(mknodes, kls_name), parent=parent)
            if parent is not None
            else getattr(mknodes, kls_name)
        )
        for kls_name in mknodes.__all__
    }


def set_markdown_exec_namespace(variables: dict[str, Any], namespace: str = "mknodes"):
    if util.find_spec("markdown_exec"):
        from markdown_exec.formatters import python

        python._sessions_globals[namespace] = variables


if __name__ == "__main__":
    macros = get_mknodes_macros(parent=None)
    print(macros["MkCode"])
