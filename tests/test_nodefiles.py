from __future__ import annotations

import pytest

import mknodes as mk

from mknodes.utils import classhelpers


def example_instances():
    page = mk.MkPage.with_context()
    for cls in classhelpers.list_subclasses(mk.MkNode):
        if cls.nodefile:
            yield from cls.nodefile.iter_example_instances(page)


@pytest.mark.parametrize("node", example_instances(), ids=lambda x: x.__class__.__name__)
def test_if_example_can_get_rendered(node):
    if nodefile := node.nodefile:
        for v in nodefile.examples.values():
            if "jinja" in v:
                node.env.render_string(v["jinja"])
            if "python" in v:
                node.env.evaluate(v["python"])


@pytest.mark.parametrize("node", example_instances(), ids=lambda x: x.__class__.__name__)
def test_if_template_output_equals_code_output(node: mk.MkNode):
    if (nodefile := node.nodefile) and (output := nodefile.output):
        for v in output.values():
            result = node.env.render_string(v["template"], dict(node=node))
            assert result == node._to_markdown()
