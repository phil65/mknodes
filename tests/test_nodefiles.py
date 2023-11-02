from __future__ import annotations

import pytest

import mknodes as mk

from mknodes.utils import classhelpers


def example_instances():
    theme = mk.Theme("mkdocs")
    proj = mk.Project(theme=theme)
    page = mk.MkPage(context=proj.context)
    for cls in classhelpers.iter_subclasses(mk.MkNode):
        if cls.nodefile:
            yield from cls.nodefile.iter_example_instances(page)


@pytest.mark.parametrize("node", example_instances(), ids=lambda x: x.__class__.__name__)
def test_examples(node):
    if nodefile := node.nodefile:
        for v in nodefile.examples.values():
            text = v["jinja"] if "jinja" in v else v["python"]
            node.env.render_string(text)


@pytest.mark.parametrize("node", example_instances(), ids=lambda x: x.__class__.__name__)
def test_output(node: mk.MkNode):
    if (nodefile := node.nodefile) and (output := nodefile.output):
        for v in output.values():
            result = node.env.render_string(v["template"], dict(node=node))
            assert result == node._to_markdown()
