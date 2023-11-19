from __future__ import annotations

from typing import TYPE_CHECKING

import jinja2

from mknodes.jinja import nodeenvironment


if TYPE_CHECKING:
    import types

    import griffe

    import mknodes as mk


@jinja2.pass_environment
def get_link(
    env: nodeenvironment.NodeEnvironment,
    target,
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
def get_url(env: nodeenvironment.NodeEnvironment, target) -> str:
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


def apply_mod(node: mk.MkNode, mod_name: str, **kwargs) -> mk.MkNode:
    """Apply a mod to given node.

    Arguments:
        node: The node to add a mod to
        mod_name: The name of the modification to add
        kwargs: Keyword arguments for the mod ctor
    """
    node.mods.add_mod(mod_name, **kwargs)
    return node
