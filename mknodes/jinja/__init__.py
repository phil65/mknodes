"""MkNodes jinja environment and helpers."""

from __future__ import annotations

import functools

import jinjarope
import tomli_w
from jinjarope import inspectfilters

from mknodes import paths
from mknodes.utils import classhelpers, inspecthelpers, yamlhelpers


def setup_env(env: jinjarope.Environment):
    """Used as extension point for the jinjarope environment.

    Arguments:
        env: The jinjarope environment to extend
    """
    node_klasses = get_nodes()
    env.globals |= dict(mk=node_klasses, _mk=node_klasses)
    env.globals |= {"inspecthelpers": inspecthelpers, "classhelpers": classhelpers}
    path = paths.RESOURCES / "filters.toml"
    env.load_jinja_file(path)
    env.filters |= node_klasses
    env.filters |= {
        "dump_yaml": yamlhelpers.dump_yaml,
        "dump_toml": tomli_w.dumps,
        "load_yaml": yamlhelpers.load_yaml,
    }


@functools.cache
def get_nodes():
    import mknodes as mk

    return {k.__name__: k for k in inspectfilters.list_subclasses(mk.MkNode)}
