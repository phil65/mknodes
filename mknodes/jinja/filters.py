from __future__ import annotations

from typing import TYPE_CHECKING, Any

import jinja2
from jinja2 import runtime
from jinjarope import htmlfilters
from markupsafe import Markup


if TYPE_CHECKING:
    import types

    import griffe

    import mknodes as mk
    from mknodes.info.linkprovider import LinkableType
    from mknodes.jinja import nodeenvironment


@jinja2.pass_environment
def get_link(
    env: nodeenvironment.NodeEnvironment,
    target: LinkableType,
    title: str | None = None,
) -> str:
    """Return a markdown link for given target.

    Target can be a class, a module, a MkPage, MkNav or a string.

    Arguments:
        env: jinja environment
        target: The thing to link to
        title: The title to use for the link
    """
    return env.node.ctx.links.get_link(target, title)


@jinja2.pass_environment
def get_url(env: nodeenvironment.NodeEnvironment, target: LinkableType) -> str:
    """Return a markdown link for given target.

    Target can be a class, a module, a MkPage, MkNav or a string.

    Arguments:
        env: jinja environment
        target: The thing to link to
    """
    return env.node.ctx.links.get_url(target)


@jinja2.pass_environment
def link_for_class(
    env: nodeenvironment.NodeEnvironment,
    kls: type | str | griffe.Class,
) -> str:
    """Return a markdown link for given class.

    Arguments:
        env: jinja environment
        kls: Klass to get a link for
    """
    return env.node.ctx.links.link_for_klass(kls)


@jinja2.pass_environment
def link_for_module(
    env: nodeenvironment.NodeEnvironment,
    module: types.ModuleType | str | griffe.Module,
) -> str:
    """Return a markdown link for given module.

    Arguments:
        env: jinja environment
        module: Klass to get a link for
    """
    return env.node.ctx.links.link_for_module(module)


def to_html(node: mk.MkNode) -> str:
    """Return HTML for given node.

    Arguments:
        node: The node to add a mod to
    """
    return node.to_html()


def apply_mod(node: mk.MkNode, mod_name: str, **kwargs: Any) -> mk.MkNode:
    """Apply a mod to given node.

    Arguments:
        node: The node to add a mod to
        mod_name: The name of the modification to add
        kwargs: Keyword arguments for the mod ctor
    """
    node.mods.add_mod(mod_name, **kwargs)
    return node


def add_annotation(node: mk.MkNode, num: int, annotation: str) -> mk.MkNode:
    """Add an annotation to given node.

    Arguments:
        node: The node to add an annotation to
        num: The annotation number
        annotation: The annotation itself
    """
    node.annotations[num] = annotation
    return node


@jinja2.pass_context
def url(context: runtime.Context, value: str) -> str:
    """A Template filter to normalize URLs.

    Arguments:
        context: The environment context
        value: The value to normalize
    """
    url = page.url if (page := context.get("page")) else None
    return htmlfilters.normalize_url(str(value), url=url, base=context["base_url"])


@jinja2.pass_context
def script_tag(context: runtime.Context, extra_script):
    """Converts an ExtraScript value / JSResource to an HTML <script> tag line.

    Arguments:
        context: The environment context
        extra_script: The object to convert to a <script> tag
    """
    html = '<script src="{0}"'
    if not isinstance(extra_script, str):
        if extra_script.type:
            html += ' type="{1.type}"'
        if extra_script.defer:
            html += " defer"
        if extra_script.async_:
            html += " async"
    html += "></script>"
    return Markup(html).format(url(context, str(extra_script)), extra_script)
