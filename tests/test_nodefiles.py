from __future__ import annotations

import contextlib

import pytest

import mknodes as mk

from mknodes.utils import classhelpers


def node_instances():
    theme = mk.Theme("mkdocs")
    proj = mk.Project(theme=theme)
    for cls in classhelpers.iter_subclasses(mk.MkNode):
        try:
            yield cls(context=proj.context)
        except TypeError:
            with contextlib.suppress(Exception):
                yield cls("mknodes", context=proj.context)


@pytest.mark.parametrize("node", node_instances())
def test_examples(node):
    try:
        nodefile = node.get_nodefile()
    except FileNotFoundError:
        pass
    else:
        for v in nodefile.examples.values():
            node.env.render_string(v["jinja"])


@pytest.mark.parametrize("node", node_instances())
def test_output(node: mk.MkNode):
    try:
        nodefile = node.get_nodefile()
    except FileNotFoundError:
        pass
    else:
        if output := nodefile.output:
            for v in output.values():
                result = node.env.render_string(v["template"], dict(node=node))
                assert result == str(node)
