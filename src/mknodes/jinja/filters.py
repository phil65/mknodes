from typing import TYPE_CHECKING, Any

import jinja2
from jinjarope import htmlfilters
from markupsafe import Markup


if TYPE_CHECKING:
    from jinja2 import runtime

    import mknodes as mk
    from mknodes.info.linkprovider import LinkableType
    from mknodes.jinja.nodeenvironment import NodeEnvironment
    from mknodes.utils.resources import JSFile, JSText


@jinja2.pass_environment
def get_link(env: NodeEnvironment, target: LinkableType, title: str | None = None) -> str:
    """Return a markdown link for given target.

    Target can be a class, a module, a MkPage, MkNav or a string.

    Args:
        env: jinja environment
        target: The thing to link to
        title: The title to use for the link
    """
    import mknodes as mk

    node = env.node
    page = node if isinstance(node, mk.MkPage) else node.parent_page
    return env.node.ctx.links.get_link(target, title, from_page=page)


@jinja2.pass_environment
def get_url(env: NodeEnvironment, target: LinkableType) -> str:
    """Return a markdown link for given target.

    Target can be a class, a module, a MkPage, MkNav or a string.

    Args:
        env: jinja environment
        target: The thing to link to
    """
    return env.node.ctx.links.get_url(target)


def to_html(node: mk.MkNode) -> str:
    """Return HTML for given node.

    Args:
        node: The node to add a mod to
    """
    return node.to_html()


def apply_mod(node: mk.MkNode, mod_name: str, **kwargs: Any) -> mk.MkNode:
    """Apply a mod to given node.

    Args:
        node: The node to add a mod to
        mod_name: The name of the modification to add
        kwargs: Keyword arguments for the mod ctor
    """
    node.mods.add_mod(mod_name, **kwargs)
    return node


def add_annotation(node: mk.MkNode, num: int, annotation: str) -> mk.MkNode:
    """Add an annotation to given node.

    Args:
        node: The node to add an annotation to
        num: The annotation number
        annotation: The annotation itself
    """
    node.annotations[num] = annotation
    return node


@jinja2.pass_context
def url(context: runtime.Context, value: str) -> str:
    """A Template filter to normalize URLs.

    Args:
        context: The environment context
        value: The value to normalize
    """
    url = page.url if (page := context.get("page")) else None
    return htmlfilters.normalize_url(str(value), url=url, base=context["base_url"])


@jinja2.pass_context
def script_tag(context: runtime.Context, extra_script: str | JSFile | JSText | Any) -> Markup:
    """Converts an extra script config value / JSResource to an HTML <script> tag line.

    Args:
        context: The environment context
        extra_script: The object to convert to a <script> tag
    """
    html = '<script src="{0}"'
    if not isinstance(extra_script, str):
        # bw compat for now, should all be type at some point.
        if hasattr(extra_script, "typ") and extra_script.typ:  # pyright: ignore[reportAttributeAccessIssue]
            html += ' type="{1.type}"'  # type or typ?
        if hasattr(extra_script, "type") and extra_script.type:  # pyright: ignore[reportAttributeAccessIssue]
            html += ' type="{1.type}"'  # type or typ?
        if extra_script.defer:
            html += " defer"
        if extra_script.async_:
            html += " async"
    html += "></script>"
    string = url(context, str(extra_script))
    return Markup(html).format(string, extra_script)
