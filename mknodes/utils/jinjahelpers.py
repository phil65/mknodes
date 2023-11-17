from __future__ import annotations

import functools

from importlib import util
from typing import Any

import jinja2

from jinja2 import runtime
import jinjarope
from markupsafe import Markup
import tomli_w

from mknodes.utils import (
    classhelpers,
    icons,
    inspecthelpers,
    log,
    pathhelpers,
    yamlhelpers,
)


logger = log.get_logger(__name__)


@jinja2.pass_context
def url_filter(context: runtime.Context, value: str) -> str:
    """A Template filter to normalize URLs."""
    url = page.url if (page := context.get("page")) else None
    return pathhelpers.normalize_url(str(value), url=url, base=context["base_url"])


@jinja2.pass_context
def script_tag_filter(context: runtime.Context, extra_script):
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


def setup_env(env: jinjarope.Environment):
    """Used as extension point for the jinjarope environment.

    Arguments:
        env: The jinjarope environment to extend
    """
    node_klasses = get_nodes()
    env.globals |= dict(mk=node_klasses, _mk=node_klasses)
    env.globals |= {"inspecthelpers": inspecthelpers, "classhelpers": classhelpers}
    env.filters |= node_klasses
    env.filters |= {
        "get_icon_svg": icons.get_icon_svg,
        "get_emoji_slug": icons.get_emoji_slug,
        "get_doc": inspecthelpers.get_doc,
        "to_class": classhelpers.to_class,
        "dump_yaml": yamlhelpers.dump_yaml,
        "dump_toml": tomli_w.dumps,
        "load_yaml": yamlhelpers.load_yaml,
        "url": url_filter,
        "script_tag": script_tag_filter,
    }


@functools.cache
def get_nodes():
    import mknodes as mk

    return {k.__name__: k for k in classhelpers.list_subclasses(mk.MkNode)}


def set_markdown_exec_namespace(variables: dict[str, Any], namespace: str = "mknodes"):
    if util.find_spec("markdown_exec"):
        from markdown_exec.formatters import python

        python._sessions_globals[namespace] = variables


if __name__ == "__main__":
    nodes = get_nodes()
    print(nodes)
