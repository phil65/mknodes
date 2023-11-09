from __future__ import annotations

import functools

from importlib import util
from typing import Any

import jinja2
import jinjarope

from jinjarope import envglobals
from markupsafe import Markup
import tomli_w

from mknodes import paths
from mknodes.utils import (
    classhelpers,
    helpers,
    icons,
    inspecthelpers,
    log,
    pathhelpers,
    yamlhelpers,
)


logger = log.get_logger(__name__)


@jinja2.pass_context
def url_filter(context, value: str) -> str:
    """A Template filter to normalize URLs."""
    url = page.url if (page := context.get("page")) else None
    return pathhelpers.normalize_url(str(value), url=url, base=context["base_url"])


@jinja2.pass_context
def script_tag_filter(context, extra_script):
    """Converts an ExtraScript value to an HTML <script> tag line."""
    html = '<script src="{0}"'
    if not isinstance(extra_script, str):
        if extra_script.type:
            html += ' type="{1.type}"'
        if extra_script.defer:
            html += " defer"
        if extra_script.async_:
            html += " async"
    html += "></script>"
    return Markup(html).format(url_filter(context, str(extra_script)), extra_script)


ENV_GLOBALS = {
    "log": log.log_stream.getvalue,
    "inspecthelpers": inspecthelpers,
    "classhelpers": classhelpers,
    "resources_dir": paths.RESOURCES,
}
ENV_FILTERS = {
    "get_icon_svg": icons.get_icon_svg,
    "get_emoji_slug": icons.get_emoji_slug,
    "styled": helpers.styled,
    "batched": helpers.batched,
    "get_hash": helpers.get_hash,
    "get_doc": inspecthelpers.get_doc,
    "to_class": classhelpers.to_class,
    "dump_yaml": yamlhelpers.dump_yaml,
    "dump_toml": tomli_w.dumps,
    "load_yaml": yamlhelpers.load_yaml,
    "url": url_filter,
    "script_tag": script_tag_filter,
} | envglobals.ENV_FILTERS  # envglobals filters required for MkDocs themes


@jinjarope.Environment.register_globals
@functools.cache
def get_globals():
    import mknodes as mk

    node_klasses = {k.__name__: k for k in classhelpers.list_subclasses(mk.MkNode)}
    return dict(mk=node_klasses, _mk=node_klasses) | ENV_GLOBALS


@jinjarope.Environment.register_filters
@functools.cache
def get_filters():
    import mknodes as mk

    node_klasses = {k.__name__: k for k in classhelpers.list_subclasses(mk.MkNode)}
    return ENV_FILTERS | node_klasses


def set_markdown_exec_namespace(variables: dict[str, Any], namespace: str = "mknodes"):
    if util.find_spec("markdown_exec"):
        from markdown_exec.formatters import python

        python._sessions_globals[namespace] = variables


if __name__ == "__main__":
    a = get_filters()
    print(a["evaluate"])
