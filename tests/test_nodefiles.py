from __future__ import annotations

import contextlib

import pytest

import mknodes as mk

from mknodes.utils import classhelpers


def node_instances():
    for cls in classhelpers.iter_subclasses(mk.MkNode):
        with contextlib.suppress(TypeError):
            yield cls.with_default_context()


@pytest.mark.parametrize("all_nodes", node_instances())
def test_examples(all_nodes):
    for node in all_nodes:
        try:
            nodefile = node.get_nodefile()
            for v in nodefile.examples.values():
                result = node.env.render_string(v["jinja"])
                assert result
            # node.env.render_string()
        except (FileNotFoundError, TypeError):
            pass


# theme = mk.MaterialTheme()
# proj = mk.Project(theme=theme)
# test_examples(proj)
