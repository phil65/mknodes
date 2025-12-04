"""MkNodes jinja environment and helpers."""

from __future__ import annotations

import functools
import logging

import tomli_w
from jinjarope import inspectfilters
import yamling

from mknodes import paths
from mknodes.utils import classhelpers, inspecthelpers
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import jinjarope
    import mknodes as mk

logger = logging.getLogger(__name__)


def setup_env(env: jinjarope.Environment) -> None:
    """Used as extension point for the jinjarope environment.

    Args:
        env: The jinjarope environment to extend
    """
    try:
        node_klasses = get_nodes()
        env.globals |= dict(mk=node_klasses, _mk=node_klasses)  # pyright: ignore[reportAttributeAccessIssue]
        env.globals |= {"inspecthelpers": inspecthelpers, "classhelpers": classhelpers}  # pyright: ignore[reportAttributeAccessIssue]
        path = paths.RESOURCES / "filters.toml"
        env.load_jinja_file(path)
        env.filters |= node_klasses
        env.filters |= {
            "dump_yaml": yamling.dump_yaml,
            "dump_toml": tomli_w.dumps,
            "load_yaml": yamling.load_yaml,
        }
    except Exception as e:  # noqa: BLE001
        logger.warning("Could not setup jinjarope environment: %s", e)


@functools.cache
def get_nodes() -> dict[str, type[mk.MkNode]]:
    import mknodes as mk

    return {k.__name__: k for k in inspectfilters.list_subclasses(mk.MkNode)}
