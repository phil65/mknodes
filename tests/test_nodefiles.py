from __future__ import annotations

import contextlib

import pytest

import mknodes as mk

from mknodes.utils import classhelpers


def node_instances():
    theme = mk.Theme("mkdocs")
    proj = mk.Project(theme=theme)
    for cls in classhelpers.iter_subclasses(mk.MkNode):
        with contextlib.suppress(TypeError):
            yield cls(context=proj.context)


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
def test_output(node):
    try:
        nodefile = node.get_nodefile()
    except FileNotFoundError:
        pass
    else:
        if (output := nodefile.get("output")) and (xml := output.get("xml")):
            raise ValueError(xml)
            result = node.env.render_string(xml)
            assert result


# theme = mk.MaterialTheme()
# proj = mk.Project(theme=theme)
# test_output(proj)
